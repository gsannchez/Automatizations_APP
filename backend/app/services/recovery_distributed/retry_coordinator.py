"""
app/services/recovery_distributed/retry_coordinator.py

Centralised exponential-backoff retry coordinator for distributed tasks.
Uses Redis sorted sets as a delay queue so retries survive worker restarts.
"""
import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

RETRY_QUEUE_KEY = "retry_delay_queue"
MAX_GLOBAL_RETRIES = 5


class RetryCoordinator:
    """
    Stores failed tasks in a Redis sorted set keyed by their
    scheduled retry timestamp, then requeues them when due.

    Usage:
        await coordinator.schedule_retry(task_meta, attempt=1)
        # Background loop:
        await coordinator.flush_due_retries()
    """

    def __init__(self, redis_client, celery_app):
        self.redis = redis_client
        self.celery = celery_app

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def schedule_retry(
        self,
        task_meta: Dict[str, Any],
        attempt: int,
        base_delay: float = 10.0,
    ) -> Optional[float]:
        """
        Schedule a retry with exponential back-off.
        Returns the scheduled epoch timestamp, or None if max retries exceeded.
        """
        if attempt > MAX_GLOBAL_RETRIES:
            logger.error(
                f"[RetryCoordinator] Task {task_meta.get('task_id')} exceeded "
                f"{MAX_GLOBAL_RETRIES} retries — moving to DLQ."
            )
            await self._move_to_dlq(task_meta)
            return None

        delay = base_delay * (2 ** (attempt - 1))  # 10s, 20s, 40s, 80s, 160s
        run_at = time.time() + delay

        task_meta["_retry_attempt"] = attempt
        task_meta["_retry_scheduled_at"] = run_at

        await self.redis.zadd(
            RETRY_QUEUE_KEY, {json.dumps(task_meta, default=str): run_at}
        )
        logger.info(
            f"[RetryCoordinator] Scheduled retry #{attempt} for "
            f"{task_meta.get('task_name')} in {delay:.0f}s"
        )
        return run_at

    async def flush_due_retries(self) -> int:
        """
        Pop all tasks from the delay queue whose scheduled time has passed
        and requeue them in Celery. Returns the count of tasks requeued.
        """
        now = time.time()
        due = await self.redis.zrangebyscore(RETRY_QUEUE_KEY, "-inf", now)

        if not due:
            return 0

        count = 0
        for raw in due:
            try:
                task_meta = json.loads(raw)
                await self._dispatch(task_meta)
                await self.redis.zrem(RETRY_QUEUE_KEY, raw)
                count += 1
            except Exception as exc:
                logger.error(f"[RetryCoordinator] Dispatch error: {exc}")

        if count:
            logger.info(f"[RetryCoordinator] Flushed {count} due retry(ies).")
        return count

    async def pending_count(self) -> int:
        """Return the total number of tasks waiting for retry."""
        return await self.redis.zcard(RETRY_QUEUE_KEY)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _dispatch(self, task_meta: Dict[str, Any]) -> None:
        task_name = task_meta["task_name"]
        kwargs = task_meta.get("kwargs", {})
        queue = task_meta.get("queue", "recovery_queue")
        kwargs["_is_recovery"] = True
        kwargs["_retry_attempt"] = task_meta.get("_retry_attempt", 1)

        sig = self.celery.signature(task_name, kwargs=kwargs, queue=queue)
        sig.apply_async()
        logger.info(
            f"[RetryCoordinator] Dispatched retry for {task_name} → {queue}"
        )

    async def _move_to_dlq(self, task_meta: Dict[str, Any]) -> None:
        dlq_key = "dead_letter_queue"
        task_meta["_failed_at"] = time.time()
        await self.redis.rpush(dlq_key, json.dumps(task_meta, default=str))
        logger.error(
            f"[RetryCoordinator] DLQ: {task_meta.get('task_name')} "
            f"[{task_meta.get('task_id')}]"
        )
