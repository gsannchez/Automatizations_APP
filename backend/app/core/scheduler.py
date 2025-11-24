from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import logging

logger = logging.getLogger(__name__)

# Instancia global del scheduler
scheduler = AsyncIOScheduler(jobstores={"default": MemoryJobStore()})

def start_scheduler():
    """Inicia el scheduler si no está corriendo."""
    if not scheduler.running:
        scheduler.start()
        logger.info("🕒 APScheduler started.")

def stop_scheduler():
    """Detiene el scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("🛑 APScheduler stopped.")
