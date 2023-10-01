import logging
from pathlib import Path

from collections.abc import Sized, Iterable

logger = logging.getLogger(__name__)


def is_iterable_empty(t: Iterable):
    """Check if a tuple is empty. ie: has no values or all being None."""
    empty = True
    for e in t:
        empty = empty and (e is None or (isinstance(e, Sized) and len(e) == 0))
        if not empty:
            break
    return empty


from .startup_checks import (
    pre_startup_check,
    pre_startup_db_migration,
    pre_startup_logconf,
)

pre_startup_check()
pre_startup_db_migration()
pre_startup_logconf()

from our_celery_manager.app.service.celery.cluster_listener import (
    CeleryClusterInformationSubject,
    CeleryClusterInformationObserver,
)

celery_events_subject = CeleryClusterInformationSubject()
