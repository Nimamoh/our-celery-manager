from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from .example import Example

from .task.TaskResult import TaskResult