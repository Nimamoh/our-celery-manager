"""Une application celery de test qui peut être utilisé comme worker"""

from celery import Celery
from celery import current_task
import time

from .Settings import Settings

settings = Settings()  # type: ignore
celery = Celery(
    "test_app", broker=settings.broker, backend=settings.backend, result_extended=True
)

@celery.task
def add(x, y):
    return x + y


@celery.task
def will_fail(msg: str):
    raise Exception(msg)


@celery.task
def ohlong(seconds: int = 5):
    time.sleep(seconds)


# region: task with parent
@celery.task
def add_n_times(n=5, a=1, b=2):
    curr_taskid = current_task.request.id
    for _ in range(n):
        # child_add.delay(a, b, ocm_parent_id=curr_taskid)
        child_add.delay(a, b, f'ocm_parent_id:{curr_taskid}')

@celery.task
def child_add(x, y):
    return x + y
# endregion