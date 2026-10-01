"""Purge Celery queues and reset stuck videos in PostgreSQL.

Usage (from backend/):
    python scripts/clear_pipeline_queue.py
    python scripts/clear_pipeline_queue.py --requeue-one <video-uuid>
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import redis
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from app.core.database import sync_engine


def purge_redis(client: redis.Redis) -> dict:
    stats = {"cpu_queue": 0, "gpu_queue": 0, "upload_queue": 0}
    for name in ("cpu_queue", "gpu_queue", "upload_queue"):
        stats[name] = client.delete(name)
    client.delete("unacked", "unacked_index")
    try:
        client.delete("global_gpu_lock")
    except Exception:
        pass
    client.delete("autovideo:celery:worker_alive")
    return stats


def reset_videos(session: Session, only_non_done: bool = True) -> int:
    where = "WHERE is_deleted = false"
    if only_non_done:
        where += " AND pipeline_state NOT IN ('DONE')"
    result = session.execute(
        text(f"""
            UPDATE video
            SET status = 'QUEUED',
                pipeline_state = 'QUEUED',
                progress = 0,
                error_message = NULL,
                error_step = NULL
            {where}
        """)
    )
    session.commit()
    return result.rowcount or 0


def main():
    parser = argparse.ArgumentParser(description="Clear Celery queues and reset videos")
    parser.add_argument(
        "--keep-done",
        action="store_true",
        help="Only reset non-DONE videos (default behavior)",
    )
    parser.add_argument(
        "--requeue-one",
        type=str,
        default=None,
        help="After purge, enqueue a single video id",
    )
    args = parser.parse_args()

    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    queue_stats = purge_redis(client)
    print("Redis purged:", queue_stats)

    with Session(sync_engine) as session:
        count = reset_videos(session, only_non_done=True)
        print(f"Videos reset to QUEUED: {count}")

    if args.requeue_one:
        from app.tasks.pipeline import process_video_workflow

        process_video_workflow.delay(args.requeue_one)
        print(f"Re-queued single video: {args.requeue_one}")
    else:
        print("No tasks re-queued. Create/generate one video when the worker is running.")


if __name__ == "__main__":
    main()
