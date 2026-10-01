import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from sqlmodel import select, delete, text
from app.core.database import get_async_session
from app.models.template import Template
from app.models.generated_video import GeneratedVideo
from app.models.user import User

# Display order in UI (lower = first)
_CREATIVE_TEMPLATE_DEFS = [
    {
        "sort_order": 10,
        "name": "Midnight Horror Tales",
        "description": "Short creepypasta stories. Visually disturbing and atmospheric.",
        "platform": "tiktok",
        "style_config": {
            "duration": 50,
            "voice": "fable",
            "music_style": "horror_dissonant",
            "image_style": "eerie_surrealism",
            "prompt_template": (
                "Write a 50-second horror story about {topic}. "
                "Describe a situation where the main character realizes they are not alone. "
                "The final sentence should leave the viewer with a cold chill."
            ),
        },
    },
    {
        "sort_order": 20,
        "name": "Stoic Wisdom Hub",
        "description": "Philosophical and motivational shorts. Minimalist and profound visuals.",
        "platform": "tiktok",
        "style_config": {
            "duration": 45,
            "voice": "shimmer",
            "music_style": "peaceful_lofi",
            "image_style": "minimalist_art",
            "prompt_template": (
                "Write a 45-second script about {topic} from a Stoic perspective. "
                "Address the viewer directly: 'Your perception of {topic} is what's hurting you, not the thing itself.' "
                "End with a call to action to focus on what they can control."
            ),
        },
    },
    {
        "sort_order": 30,
        "name": "Daily Business Hacks",
        "description": "Productivity tips and financial advice for entrepreneurs. Professional.",
        "platform": "instagram",
        "style_config": {
            "duration": 30,
            "voice": "echo",
            "music_style": "upbeat_corporate",
            "image_style": "modern_office_clean",
            "prompt_template": (
                "Create a 30-second 'business hack' script about {topic}. "
                "Start with a common mistake: 'Most entrepreneurs fail at {topic} because of this...'. "
                "Provide a better strategy and ask people to share their thoughts below."
            ),
        },
    },
    {
        "sort_order": 40,
        "name": "Deep Mystery Chronicles",
        "description": "Suspenseful storytelling about unsolved mysteries and urban legends. Cinematic & dark.",
        "platform": "youtube",
        "style_config": {
            "duration": 55,
            "voice": "onyx",
            "music_style": "dark_ambient",
            "image_style": "photorealistic_cinematic",
            "prompt_template": (
                "Create a gripping 55-second script about {topic}. "
                "Start with a hook: 'The secret they didn't want you to know about {topic} is finally out...'. "
                "Use a slow, methodical pace. Reveal a shocking fact in the middle."
            ),
        },
    },
    {
        "sort_order": 50,
        "name": "Future Tech Pulse",
        "description": "Fast-paced updates on AI, gadgets, and future tech. High energy.",
        "platform": "youtube",
        "style_config": {
            "duration": 60,
            "voice": "nova",
            "music_style": "cyberpunk_synth",
            "image_style": "sci_fi_neon",
            "prompt_template": (
                "Generate a high-energy tech update about {topic}. "
                "Use short, punchy sentences. Mention 3 ways {topic} is disrupting the current market. "
                "End with: 'Are you ready for the evolution? Subscribe for more tech pulses.'."
            ),
        },
    },
]


async def seed_creative_templates():
    async for session in get_async_session():
        print("Performing deep clean of templates and related data...")
        try:
            await session.execute(text("TRUNCATE TABLE videojob, video, template RESTART IDENTITY CASCADE"))
            await session.commit()
            print("Cleanup successful.")
        except Exception as e:
            print(f"Truncate failed, trying manual delete: {e}")
            await session.rollback()
            from app.models.video_job import VideoJob

            await session.execute(delete(VideoJob))
            await session.execute(delete(GeneratedVideo))
            await session.execute(delete(Template))
            await session.commit()

        result = await session.execute(select(User))
        user = result.scalars().first()
        if not user:
            print("No users found. Please register first.")
            return

        for spec in _CREATIVE_TEMPLATE_DEFS:
            style_config = dict(spec["style_config"])
            t = Template(
                name=spec["name"],
                description=spec["description"],
                platform=spec["platform"],
                style_config=style_config,
                sort_order=spec["sort_order"],
            )
            session.add(t)
            print(f"Adding professional template ({spec['sort_order']}): {t.name}")

        await session.commit()
        print("\nSUCCESS: Dashboard cleaned and 5 premium templates installed (ordered).")
        break


if __name__ == "__main__":
    asyncio.run(seed_creative_templates())
