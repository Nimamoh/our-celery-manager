from sqlalchemy import select
from celery.backends.database.models import Task
from models.TaskResult import TaskResult

from tasks_queue import app as celeryapp

def get_all_results() -> list[TaskResult]:

    stmt = select(Task.task_id, Task.status)
    session = celeryapp.backend.ResultSession()

    result = session.execute(stmt)

    results = []
    for row in result:
        (id, status) = row
        results.append(TaskResult(id, status))

    return results