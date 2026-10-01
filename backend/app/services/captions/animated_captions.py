import os
from typing import List, Dict
from .caption_styles import CaptionStyleEngine, CaptionStyleProfile

class AnimatedCaptionsEngine:
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time to ASS format: H:MM:SS.cs"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds % 1) * 100))
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    @staticmethod
    def generate_ass_file(timings: List[Dict], profile: CaptionStyleProfile, output_path: str, max_words_per_line: int = 4):
        """
        Generates an Advanced SubStation Alpha (.ass) file with karaoke-like effects 
        or chunked highlighting for dynamic captions.
        """
        ass_content = CaptionStyleEngine.get_ass_style(profile)
        
        # Chunk timings into lines
        lines = []
        for i in range(0, len(timings), max_words_per_line):
            lines.append(timings[i:i + max_words_per_line])
            
        for line_timings in lines:
            line_start = line_timings[0]['start']
            line_end = line_timings[-1]['end']
            
            # Format ASS event
            start_str = AnimatedCaptionsEngine._format_time(line_start)
            end_str = AnimatedCaptionsEngine._format_time(line_end)
            
            # Build the text with dynamic effects (e.g., color highlighting word by word)
            # Standard ASS karaoke is {\k(duration_in_cs)}
            # But for TikTok style we often highlight one word at a time.
            # A simple trick is to duplicate the line multiple times, highlighting a different word each time
            # For simplicity, we'll use ASS tags to change color mid-line, or generate multiple events.
            
            # Generating multiple events, one per highlighted word
            for i, target_word in enumerate(line_timings):
                # The duration of this specific highlight
                hl_start = target_word['start']
                hl_end = target_word['end']
                
                hl_start_str = AnimatedCaptionsEngine._format_time(hl_start)
                hl_end_str = AnimatedCaptionsEngine._format_time(hl_end)
                
                text_parts = []
                for j, word_info in enumerate(line_timings):
                    if i == j:
                        # Highlighted word (e.g., yellow)
                        text_parts.append(f"{{\\c&H00FFFF&}}{word_info['word']}{{\\c&HFFFFFF&}}")
                    else:
                        # Normal word (white)
                        text_parts.append(word_info['word'])
                        
                dialogue_text = " ".join(text_parts)
                # ASS Event format: Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
                ass_content += f"Dialogue: 0,{hl_start_str},{hl_end_str},Default,,0,0,0,,{dialogue_text}\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
            
        return output_path
