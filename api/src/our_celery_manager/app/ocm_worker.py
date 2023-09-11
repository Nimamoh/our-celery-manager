"""A worker for our-celery-manager related tasks"""

import logging
from celery.states import FAILURE
from sqlalchemy import delete

from datetime import datetime, timedelta

from celery.backends.database.models import TaskExtended
from celery import Celery

from .settings import settings

celery = Celery(
    "tasks", broker=settings.broker, backend=settings.backend, result_extended=True
)

logger = logging.getLogger(__name__)

@celery.task(name="ocm_cleanup_backend")
def ocm_cleanup_backend(being_older_than_days: int, only_failures=True):
    """Task similar to celery cleanup backend except it accepts more options"""

    result_backend_addr = settings.hiding_passwords().backend

    logger.info(
        f"Cleaning tasks in {result_backend_addr} which are older than {being_older_than_days} days"
        ". Only cleaning failures." if only_failures else ""
    )

    if only_failures is False:
        raise NotImplementedError("Only 'only_failures' as True is supported")

    older_than = datetime.now() - timedelta(being_older_than_days)
    logger.debug(f"Cleaning tasks which date_done are older than {older_than}")

    stmt = (
        delete(TaskExtended)
        .where(TaskExtended.status == FAILURE)
        .where(TaskExtended.date_done < older_than)
    )
    session = celery.backend.ResultSession()
    result = session.execute(stmt)
    logger.info(f"Successfully deleted {result.rowcount} rows")
    session.commit()


    