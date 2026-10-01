"""
app/services/recovery_distributed/task_recovery.py

Detects and requeues incomplete or orphaned Celery tasks
by cross-referencing active worker state against the database.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Maximum age before a STARTED task is considered orphaned
ORPHAN_THRESHOLD_MINUTES = 30


class TaskRecovery:
    """
    Scans the database for tasks stuck in STARTED/PENDING state
    and requeues them via Celery if the originating worker is dead.
    """

    def __init__(self, celery_app, session, redis_client):
        self.celery = celery_app
        self.session = session
        self.redis = redis_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_recovery_sweep(self) -> Dict[str, Any]:
        """
        Full recovery sweep:
        1. Fetch active workers from Celery control.
        2. Identify orphaned tasks in the DB.
        3. Requeue each orphaned task.
        """
        active_workers = self._get_active_worker_ids()
        orphans = await self._find_orphaned_tasks(active_workers)

        requeued = []
        failed = []

        for task_meta in orphans:
            try:
                await self._requeue_task(task_meta)
                requeued.append(task_meta["task_id"])
            except Exception as exc:
                logger.error(
                    f"[TaskRecovery] Failed to requeue {task_meta['task_id']}: {exc}"
                )
                failed.append(task_meta["task_id"])

        logger.info(
            f"[TaskRecovery] Sweep complete — requeued={len(requeued)}, failed={len(failed)}"
        )
        return {"requeued": requeued, "failed": failed}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_active_worker_ids(self) -> List[str]:
        """Ask Celery control plane for alive worker hostnames."""
        try:
            inspect = self.celery.control.inspect(timeout=5)
            stats = inspect.stats() or {}
            return list(stats.keys())
        except Exception as exc:
            logger.warning(f"[TaskRecovery] Could not reach Celery control: {exc}")
            return []

    async def _find_orphaned_tasks(self, active_workers: List[str]) -> List[Dict]:
        """
        Query Redis/Celery backend for tasks stuck in STARTED state
        beyond the orphan threshold that are not on any live worker.
        """
        threshold = datetime.now(timezone.utc) - timedelta(
            minutes=ORPHAN_THRESHOLD_MINUTES
        )
        orphans: List[Dict] = []

        try:
            # Scan Celery task result backend keys (format depends on backend)
            keys = await self.redis.keys("celery-task-meta-*")
            for key in keys:
                raw = await self.redis.get(key)
                if not raw:
                    continue

                import json

                meta = json.loads(raw)
                status = meta.get("status", "")
                date_done = meta.get("date_done")

                if status != "STARTED":
                    continue

                # Parse timestamp if available
                if date_done:
                    try:
                        ts = datetime.fromisoformat(date_done.rstrip("Z")).replace(
                            tzinfo=timezone.utc
                        )
                        if ts > threshold:
                            continue  # Still within acceptable window
                    except ValueError:
                        pass

                task_id = key.decode().replace("celery-task-meta-", "")
                worker = meta.get("result", {}).get("hostname", "") if isinstance(meta.get("result"), dict) else ""

                if worker and worker in active_workers:
                    continue  # Task is alive on a healthy worker

                orphans.append(
                    {
                        "task_id": task_id,
                        "task_name": meta.get("task_name", "unknown"),
                        "kwargs": meta.get("kwargs", {}),
                        "queue": meta.get("queue", "cpu_queue"),
                    }
                )
        except Exception as exc:
            logger.error(f"[TaskRecovery] Error scanning orphaned tasks: {exc}")

        logger.info(f"[TaskRecovery] Found {len(orphans)} orphaned task(s).")
        return orphans

    async def _requeue_task(self, task_meta: Dict) -> None:
        """Send the orphaned task back to its original queue."""
        task_name = task_meta["task_name"]
        kwargs = task_meta.get("kwargs", {})
        queue = task_meta.get("queue", "recovery_queue")

        # Mark kwargs with recovery flag to allow idempotency guards
        kwargs["_is_recovery"] = True

        signature = self.celery.signature(
            task_name,
            kwargs=kwargs,
            queue=queue,
        )
        signature.apply_async()

        logger.info(
            f"[TaskRecovery] Requeued {task_name} [{task_meta['task_id']}] → {queue}"
        )
