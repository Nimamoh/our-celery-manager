"""A worker for our-celery-manager related tasks"""

import logging
from celery.states import SUCCESS
from sqlalchemy import delete

from datetime import datetime, timedelta

from celery.backends.database.models import TaskExtended
from celery.backends.database import session_cleanup
from our_celery_manager.models.ocm import CloneEvent
from celery import Celery

from our_celery_manager.common.settings import settings
from ..db import SessionLocal # TODO: ici

celery = Celery(
    "tasks", broker=settings.broker, backend=settings.backend, result_extended=True
)

logger = logging.getLogger(__name__)

@celery.task(name="ocm_cleanup_backend")
def ocm_cleanup_backend(being_older_than_days: int, only_success=True):
    """Task similar to celery cleanup backend except it accepts more options"""

    result_backend_addr = settings.hiding_passwords().backend

    logger.info(
        f"Cleaning tasks in {result_backend_addr} which are older than {being_older_than_days} days"
        ". Only cleaning successful tasks." if only_success else ""
    )

    if only_success is False:
        raise NotImplementedError("Only 'only_success' as True is supported")

    older_than = datetime.now() - timedelta(being_older_than_days)
    logger.debug(f"Cleaning tasks which date_done are older than {older_than}")

    stmt = (
        delete(TaskExtended)
        .where(TaskExtended.status == SUCCESS)
        .where(TaskExtended.date_done < older_than)
    )

    session = celery.backend.ResultSession()
    with session_cleanup(session):
        result = session.execute(stmt)
        session.commit()
        logger.info(f"Successfully deleted {result.rowcount} tasks")

    _ocm_cleanup_cloning_events(older_than)


def _ocm_cleanup_cloning_events(older_than: datetime):
    """Cleans the cloning events"""

    logger.info(f"Cleaning cloning events which are created before {older_than}")

    stmt = (
        delete(CloneEvent)
        .where(CloneEvent.created < older_than)
    )

    session = SessionLocal()
    with session_cleanup(session):
        result = session.execute(stmt)
        session.commit()
        logger.info(f"Successfully deleted {result.rowcount} events")

