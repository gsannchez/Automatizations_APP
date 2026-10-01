import asyncio
import os
import sys
import time

sys.path.append(os.getcwd())

from sqlmodel import select
from app.core.database import get_sync_session, get_async_session
from app.models.template import Template
from app.models.generated_video import GeneratedVideo
from app.models.user import User
from app.tasks.pipeline import process_video_workflow

async def main():
    async for session in get_async_session():
        # Get or create a user
        result = await session.execute(select(User))
        user = result.scalars().first()
        if not user:
            user = User(email="test@test.com", hashed_password="hashed")
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print("Created test user.")

        # Get or create a template
        result = await session.execute(select(Template))
        template = result.scalars().first()
        if not template:
            template = Template(
                name="Test Template",
                description="Testing the pipeline",
                platform="youtube",
                style_config={"duration": 30, "voice": "echo"},
                prompt_template="Write a short engaging script about {topic}.",
                user_id=user.id
            )
            session.add(template)
            await session.commit()
            await session.refresh(template)
            print("Created test template.")

        # Create a video
        video = GeneratedVideo(
            user_id=user.id,
            template_id=template.id,
            title="Pipeline Test Video",
            platform="youtube",
            status="QUEUED",
            topic="The secret history of the pyramids",
            style_config={}
        )
        session.add(video)
        await session.commit()
        await session.refresh(video)
        print(f"Created video ID: {video.id}")

        # Trigger workflow
        print("Triggering celery workflow...")
        process_video_workflow.delay(str(video.id))

        print("Polling database for video status...")
        while True:
            await session.refresh(video)
            print(f"Current status: {video.status}")
            if video.status in ("DONE", "FAILED"):
                print(f"Pipeline finished with status: {video.status}")
                if video.error_message:
                    print(f"Error: {video.error_message}")
                break
            time.sleep(5)
        break

if __name__ == "__main__":
    asyncio.run(main())
