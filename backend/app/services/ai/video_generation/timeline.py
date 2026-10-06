"""Assemble per-scene clips into the final, broadcast-ready video.

The old assembler was a raw ``concat -c copy``: hard cuts, no music, no loudness
normalisation and a container without faststart (so the first frame only paints
after the whole file has downloaded). This module replaces it with a two-pass
encode:

  Pass 1 — join the scene clips with ``xfade`` crossfades, matching the audio
           with ``acrossfade`` and carrying the voice through
           ``VoiceEnhancer``.
  Pass 2 — optionally duck a music bed under the voice (``sidechaincompress``
           via :class:`AudioMixer`), normalise the whole mix to EBU R128
           (-14 LUFS, the streaming target), and write the final file with
           ``+faststart``.
"""
from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from typing import List, Optional

from app.core.config import settings
from app.services.audio.audio_mixer import AudioMixer
from app.services.audio.voice_enhancer import VoiceEnhancer
from app.services.storage import storage

logger = logging.getLogger(__name__)

XFADE_SECONDS = 0.4
ENCODE_TIMEOUT = 1800
# EBU R128 target for streaming platforms, shared with the per-scene voice
# normalisation so the two passes do not fight each other.
LOUDNORM = f"loudnorm=I={VoiceEnhancer.TARGET_LUFS}:TP=-1.5:LRA=11"


def _probe_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
    return float(out.stdout.strip())


def _xfade_graph(durations: List[float], transition: float) -> tuple:
    """Build the video/audio crossfade filter chain.

    Returns ``(filter_complex, video_label, audio_label)``.
    """
    parts = []
    video, audio = "[0:v]", "[0:a]"
    cumulative = durations[0]

    for i in range(1, len(durations)):
        # xfade overlaps the two clips by `transition`, so the joined clip is
        # `transition` seconds shorter than the sum of its parts.
        offset = max(cumulative - transition, 0.0)
        v_out, a_out = f"[v{i}]", f"[a{i}]"
        parts.append(
            f"{video}[{i}:v]xfade=transition=fade:duration={transition}:"
            f"offset={offset:.3f}{v_out}"
        )
        parts.append(
            f"{audio}[{i}:a]acrossfade=d={transition}:c1=tri:c2=tri{a_out}"
        )
        video, audio = v_out, a_out
        cumulative = cumulative + durations[i] - transition

    return ";".join(parts), video, audio


def _concat_graph(n: int) -> tuple:
    """Hard-cut concatenation (used when crossfades are disabled)."""
    streams = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    return f"{streams}concat=n={n}:v=1:a=1[v][a]", "[v]", "[a]"


def _join_clips(local_clips: List[str], local_out: str, transition: float) -> None:
    if len(local_clips) == 1:
        import shutil

        shutil.copyfile(local_clips[0], local_out)
        return

    if transition > 0:
        durations = [_probe_duration(p) for p in local_clips]
        graph, video, audio = _xfade_graph(durations, transition)
    else:
        graph, video, audio = _concat_graph(len(local_clips))

    cmd = ["ffmpeg", "-y"]
    for path in local_clips:
        cmd += ["-i", path]
    cmd += [
        "-filter_complex", graph,
        "-map", video, "-map", audio,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        local_out,
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=ENCODE_TIMEOUT)


def _finalise(local_in: str, local_out: str, music_path: Optional[str]) -> None:
    """Second pass: optional music bed with ducking + loudness normalisation."""
    # Video was already encoded in pass 1 — copy it through untouched.
    tail = [
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        local_out,
    ]

    if music_path and os.path.exists(music_path):
        logger.info("Mixing music bed %s with ducking", music_path)
        graph = AudioMixer.build_audio_pipeline(0, 1, bg_volume=0.18)
        graph += f";[aout]{LOUDNORM}[a_final]"
        cmd = [
            "ffmpeg", "-y",
            "-i", local_in,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex", graph,
            "-map", "0:v", "-map", "[a_final]",
            "-shortest",
            *tail,
        ]
    else:
        graph = f"[0:a]{LOUDNORM}[a_final]"
        cmd = [
            "ffmpeg", "-y",
            "-i", local_in,
            "-filter_complex", graph,
            "-map", "0:v", "-map", "[a_final]",
            *tail,
        ]

    subprocess.run(cmd, check=True, capture_output=True, timeout=ENCODE_TIMEOUT)


def assemble_timeline(
    clip_keys: List[str],
    out_key: str,
    transition: float = XFADE_SECONDS,
    music_path: Optional[str] = None,
) -> str:
    """Join scene clips from storage and write the final video to *out_key*.

    Args:
        clip_keys: storage keys of the per-scene clips, in order.
        out_key: storage key for the finished video.
        transition: crossfade duration in seconds (0 disables xfade).
        music_path: local path to a background track, or None for voice only.

    Returns:
        *out_key*.
    """
    if not clip_keys:
        raise ValueError("assemble_timeline needs at least one clip")

    if music_path is None and settings.MUSIC_BED_PATH:
        music_path = settings.MUSIC_BED_PATH

    local_clips = [storage.get_local_path(k) for k in clip_keys]
    missing = [k for k, p in zip(clip_keys, local_clips) if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"Scene clips missing from storage: {missing}")

    tmp_dir = tempfile.mkdtemp(prefix="timeline_")
    joined = os.path.join(tmp_dir, "joined.mp4")
    final_local = os.path.join(tmp_dir, "final.mp4")

    try:
        logger.info("Joining %s scene clips (transition=%.2fs)", len(local_clips), transition)
        _join_clips(local_clips, joined, transition)

        _finalise(joined, final_local, music_path)

        with open(final_local, "rb") as fh:
            storage.save(fh, out_key)

        logger.info("Timeline assembled: %s (%.1fs)", out_key, _probe_duration(final_local))
        return out_key
    finally:
        for name in (joined, final_local):
            path = os.path.join(tmp_dir, name)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass
