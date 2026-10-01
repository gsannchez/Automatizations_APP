"""Viral Styles configurations and modifiers."""
import logging
from typing import Dict, Any, List
from app.models.viral_intelligence import ViralStyle

logger = logging.getLogger(__name__)

class ViralStyleConfig:
    """Defines configurations, prompt modifiers, LUTs, and FFmpeg overlay configurations for each style."""
    
    STYLE_METADATA = {
        ViralStyle.CCTV: {
            "name": "Surveillance CCTV",
            "prompt_modifier": "cctv security camera footage, surveillance camera overlay, dated timestamp, grainy, security angle, high angle shot, realistic noise, muted colors",
            "camera_motion": "static wide lens with slight pan",
            "ffmpeg_filters": "[0:v]eq=contrast=1.15:brightness=-0.05:saturation=0.5[outv]", # Desaturate and high contrast
            "transitions": "glitch cut",
            "sound_profile": "low electric hum and tape noise",
            "captions_style": "yellow mono font on black rectangle, top-left alignment"
        },
        ViralStyle.CINEMATIC: {
            "name": "Cinematic Epic",
            "prompt_modifier": "cinematic lighting, dramatic anamorphic flares, 35mm photograph, highly detailed photorealistic, 8k, golden hour, epic composition, professional depth of field",
            "camera_motion": "slow push-in or tracking shot",
            "ffmpeg_filters": "[0:v]eq=contrast=1.05:saturation=1.1,unsharp=5:5:1.0:5:5:0.0[outv]", # Epic color and sharp details
            "transitions": "smooth crossfade",
            "sound_profile": "dramatic orchestral strings and sub bass hits",
            "captions_style": "serif white font, bottom-center alignment, italicized subtitles"
        },
        ViralStyle.DOCUMENTARY: {
            "name": "Documentary Realism",
            "prompt_modifier": "vintage National Geographic photography, real historical details, dramatic realistic lighting, film grain, Kodak Portra, authentic look, telephoto lens",
            "camera_motion": "slow Ken Burns zoom",
            "ffmpeg_filters": "[0:v]eq=contrast=1.0:brightness=0.0:saturation=0.9[outv]", # Authentic vintage lut emulation
            "transitions": "fade to black",
            "sound_profile": "minimalist acoustic guitar or deep synth drone",
            "captions_style": "Helvetica bold white text, bottom-left aligned"
        },
        ViralStyle.NEWS: {
            "name": "Breaking News Alert",
            "prompt_modifier": "breaking news live report photo, broadcast camera angle, realistic photojournalism style, paparazzi flashlight, candid high contrast",
            "camera_motion": "fast zoom-in or handheld pan",
            "ffmpeg_filters": "[0:v]eq=contrast=1.1:saturation=1.0[outv]", # Standard TV look
            "transitions": "whip pan or flash cut",
            "sound_profile": "news alert brass intro and ticking clock sound",
            "captions_style": "heavy sans font, black background bar, red/white text"
        },
        ViralStyle.TIKTOK_NATIVE: {
            "name": "TikTok Native Dynamic",
            "prompt_modifier": "highly saturated vivid colors, vertical dynamic framing, eye-level close-up shot, trending social media aesthetic, flawless portrait skin, bright studio lights",
            "camera_motion": "fast vertical pan or whip cut",
            "ffmpeg_filters": "[0:v]eq=contrast=1.1:saturation=1.25[outv]", # Pop colors
            "transitions": "fast dynamic slide",
            "sound_profile": "trending up-beat lofi or viral pop sound beats",
            "captions_style": "Montserrat extra-bold yellow text, centered, high-contrast black border, bouncy animation"
        },
        ViralStyle.HORROR: {
            "name": "Horror Found Footage",
            "prompt_modifier": "creepy dark atmosphere, night vision green filter, VHS analog glitch noise, ominous vignettes, long shadows, terrifying realistic details, flashlight beam",
            "camera_motion": "unstable shaky handheld camera",
            "ffmpeg_filters": "[0:v]colorchannelmixer=0:0:0:0:1:0:0:0:0[outv]", # Emulate nightvision green channel
            "transitions": "static VHS noise cut",
            "sound_profile": "disturbing low frequency rumblings and screech elements",
            "captions_style": "creepy hand-drawn green/red font, center-bottom aligned"
        },
        ViralStyle.MEME_REALISM: {
            "name": "Meme Realism Candid",
            "prompt_modifier": "candid shaky phone camera photograph, raw authenticity, street snapshot, flash reflection, real amateur quality, high contrast, slightly blurry movement",
            "camera_motion": "sudden camera jerks or micro zoom jumps",
            "ffmpeg_filters": "[0:v]eq=contrast=1.25:saturation=1.4[outv]", # Over-saturated "deep-fried" look
            "transitions": "instant hard cuts",
            "sound_profile": "distorted meme sound effects and bass drops",
            "captions_style": "Impact font, thick black outline, white fill, center-top alignment"
        },
        ViralStyle.BODYCAM: {
            "name": "Police Bodycam",
            "prompt_modifier": "bodycam footage, wide angle fisheye lens, police body camera, shaky running motion, gritty realism, high contrast",
            "camera_motion": "extreme shake and heavy breathing sway",
            "ffmpeg_filters": "[0:v]lenscorrection=cx=0.5:cy=0.5:k1=-0.227:k2=-0.022,eq=contrast=1.1,noise=alls=40[outv]", 
            "transitions": "glitch cut or static fade",
            "sound_profile": "heavy breathing, radio chatter, wind noise",
            "captions_style": "VCR OSD Mono font, white text on black background, top right"
        },
        ViralStyle.DASHCAM: {
            "name": "Dashcam Footage",
            "prompt_modifier": "dashcam footage, car dashboard camera, windshield glare, russian dashcam, wide angle, raw video",
            "camera_motion": "static with road vibrations",
            "ffmpeg_filters": "[0:v]eq=contrast=1.05:brightness=0.05,noise=alls=20[outv]", 
            "transitions": "hard cut",
            "sound_profile": "engine hum, road noise, muffled radio",
            "captions_style": "Arial bold, yellow text, bottom center"
        },
        ViralStyle.ANIME_EDIT: {
            "name": "Anime AMV Edit",
            "prompt_modifier": "high quality anime style, makoto shinkai aesthetic, vibrant colors, detailed anime background, studio ghibli, dynamic lighting",
            "camera_motion": "fast zoom-ins, dynamic panning, high energy",
            "ffmpeg_filters": "[0:v]eq=contrast=1.2:saturation=1.5[outv]", 
            "transitions": "whip pan, flash transition, glitch cut",
            "sound_profile": "phonk, nightcore, high energy electronic",
            "captions_style": "Stylized bold font, glowing outlines, center screen"
        },
        ViralStyle.CINEMATIC_AI: {
            "name": "Cinematic AI Reality",
            "prompt_modifier": "hyper-realistic AI generated, unreal engine 5, 8k resolution, ray tracing, cinematic lighting, ultra detailed, masterpiece",
            "camera_motion": "smooth drone shots, slow cinematic pan, steadycam tracking",
            "ffmpeg_filters": "[0:v]eq=contrast=1.15:saturation=1.05,unsharp=5:5:1.5:5:5:0.0[outv]", 
            "transitions": "cross dissolve, dip to black",
            "sound_profile": "hans zimmer style epic orchestral, deep bass",
            "captions_style": "Elegant serif font, white with subtle drop shadow, lower third"
        }
    }
    
    def get_style_config(self, style: ViralStyle) -> Dict[str, Any]:
        """Fetch settings dictionary for a given style preset.
        
        Args:
            style: The ViralStyle enum member.
            
        Returns:
            Dictionary containing style parameters.
        """
        logger.info(f"Retrieving style configuration metadata for: {style.value}")
        return self.STYLE_METADATA.get(style, self.STYLE_METADATA[ViralStyle.TIKTOK_NATIVE])
        
    def get_all_styles(self) -> List[Dict[str, Any]]:
        """Return list of all available styles with their respective identifiers and configurations."""
        return [
            {
                "style_id": style.value,
                **config
            }
            for style, config in self.STYLE_METADATA.items()
        ]
