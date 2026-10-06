"""Export a list of PIL frames to an H.264 mp4.

Prefers ``imageio`` (imageio-ffmpeg); falls back to writing a PNG sequence and
letting the system ``ffmpeg`` encode it.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Sequence

logger = logging.getLogger(__name__)


def frames_to_mp4(frames: Sequence, output_path: str, fps: int = 7) -> str:
    """Write *frames* (PIL images) to *output_path* as H.264/yuv420p."""
    try:
        import imageio

        writer = imageio.get_writer(
            output_path, fps=fps, codec="libx264", quality=8,
            macro_block_size=1, ffmpeg_params=["-pix_fmt", "yuv420p"],
        )
        try:
            for frame in frames:
                writer.append_data(_to_ndarray(frame))
        finally:
            writer.close()
        return output_path
    except Exception as exc:
        logger.warning("imageio export failed (%s); using ffmpeg PNG-sequence fallback", exc)

    return _frames_to_mp4_via_ffmpeg(frames, output_path, fps)


def _to_ndarray(frame):
    try:
        import numpy as np

        return np.asarray(frame)
    except Exception:
        # PIL image without numpy: go through a temp PNG
        return frame


def _frames_to_mp4_via_ffmpeg(frames: Sequence, output_path: str, fps: int) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("Neither imageio nor ffmpeg is available to export frames")

    with tempfile.TemporaryDirectory(prefix="svd_frames_") as tmp:
        for i, frame in enumerate(frames):
            frame.save(os.path.join(tmp, f"f_{i:05d}.png"))

        cmd = [
            ffmpeg, "-y",
            "-framerate", str(fps),
            "-i", os.path.join(tmp, "f_%05d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", "-preset", "medium",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    return output_path
