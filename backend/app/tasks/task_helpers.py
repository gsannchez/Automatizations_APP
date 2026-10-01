"""Helpers for Celery tasks invoked via .run() or .delay()."""


def raise_or_retry(task, exc: Exception, countdown: int = 30):
    """Re-raise when called synchronously; retry when executed by a worker."""
    if getattr(task.request, "called_directly", False):
        raise exc
    raise task.retry(exc=exc, countdown=countdown)
