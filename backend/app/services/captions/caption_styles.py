from enum import Enum

class CaptionStyleProfile(Enum):
    TIKTOK_CLASSIC = "tiktok_classic"
    CINEMATIC = "cinematic"
    NEWS = "news"
    HORROR = "horror"

class CaptionStyleEngine:
    @staticmethod
    def get_ass_style(profile: CaptionStyleProfile) -> str:
        """
        Returns the ASS [V4+ Styles] string for a given profile.
        These dictate font size, color, outline, and positioning.
        """
        # Base ASS Header
        header = "[Script Info]\n" \
                 "ScriptType: v4.00+\n" \
                 "PlayResX: 1080\n" \
                 "PlayResY: 1920\n\n" \
                 "[V4+ Styles]\n" \
                 "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"

        if profile == CaptionStyleProfile.TIKTOK_CLASSIC:
            # Bold, white with black outline, centered, animated karaoke
            style = "Style: Default,Arial,90,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,50,50,700,1"
        elif profile == CaptionStyleProfile.CINEMATIC:
            # Subtle, elegant font, small shadow
            style = "Style: Default,Times New Roman,60,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,50,50,200,1"
        elif profile == CaptionStyleProfile.NEWS:
            # Boxed background, lower third
            style = "Style: Default,Arial,70,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,3,4,0,2,50,50,150,1"
        elif profile == CaptionStyleProfile.HORROR:
            # Creepy font, red color, jagged
            style = "Style: Default,Courier New,85,&H000000FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,5,0,1,4,5,2,50,50,500,1"
        else:
            style = "Style: Default,Arial,80,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,0,2,50,50,600,1"

        return header + style + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
