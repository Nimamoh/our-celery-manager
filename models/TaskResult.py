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
    status: Status
    date_done: datetime