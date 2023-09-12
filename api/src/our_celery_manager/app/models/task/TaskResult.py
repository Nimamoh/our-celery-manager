from dataclasses import dataclass
from enum import StrEnum
from datetime import datetime

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

@dataclass
class TaskResult:
    task_id: str
    name: str | None
    status: Status
    date_done: datetime | None
    traceback: str | None
    queue: str | None

    args: bytes | None
    kwargs: bytes | None

    result: str | None

    nb_clones: int

@dataclass
class TaskResultPage:
    total: int
    page_number: int
    page_size: int
    data: list[TaskResult]
