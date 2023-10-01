from datetime import datetime
from enum import StrEnum

from celery.backends.database.models import TaskExtended

from our_celery_manager.app.models.dtos import OCMBaseModel


class Status(StrEnum):
    PENDING = 'PENDING'
    RECEIVED = 'RECEIVED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    REVOKED = 'REVOKED'
    REJECTED = 'REJECTED'
    RETRY = 'RETRY'
    IGNORED = 'IGNORED'

class TaskResult(OCMBaseModel):
    task_id: str
    name: str | None
    status: Status
    date_done: datetime | None
    traceback: str | None
    queue: str | None

    args: bytes | None
    kwargs: bytes | None

    result: str | None

    def __init__(self, **data):
        if 'result' in data: # Cast to string
            data['result'] = str(data['result'])
        super().__init__(**data)

    @staticmethod
    def fields_to_select(model: TaskExtended):
        return (
            model.task_id,
            model.name,
            model.status,
            model.date_done,
            model.traceback,
            model.queue,

            model.args,
            model.kwargs,
            
            model.result,
        )


class ListResultRow(TaskResult):
    clones: list["ListResultRow"]

class ListResult(OCMBaseModel):
    total: int
    page_number: int
    page_size: int
    data: list[ListResultRow]
