from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from .ocm.clone import CloneEvent

from .task.TaskResult import TaskResult