from . import logger

from app.service.celery.model import DbResultRow, SearchField, SortDirection, SortField, db_result_select_fields
from app.service.celery.mapper import map_result
from sqlalchemy import asc, desc, select, func
from celery.backends.database.models import TaskExtended
from app.models.task.TaskResult import TaskResult, TaskResultPage

from celery.result import AsyncResult

from app.tasks_queue import app as celeryapp


def result_page(
    pageSize: int,
    pageNumber: int,
    sorts: list[SortField],
    searchs: list[SearchField],
) -> TaskResultPage:
    assert pageSize < 100, "page size must be <100"
    assert pageNumber >= 0, "Page number must be >= 0"

    stmt = _stmt(sorts, searchs)
    paginated_stmt = stmt

    session = celeryapp.backend.ResultSession()

    # XXX: systeme de tag pour pouvoir compter de manière efficace ?
    # i = 0
    # while True:
    #     if i < offset:
    #         continue

    #     i+=1


    total = session.query(func.count()).select_from(stmt).scalar()
    result = session.execute(paginated_stmt)

    def map(row) -> TaskResult:
        db_row = DbResultRow(*row)
        mapped = map_result(db_row)
        return mapped
    
    data = [map(row) for row in result]
    page = TaskResultPage(
        total=total,
        page_number=pageNumber,
        page_size=pageSize,
        data = data,
    )
    return page

def _stmt(sorts: list[SortField], searchs: list[SearchField]):

    stmt = select(*db_result_select_fields)

    for sort in sorts:
        field = getattr(TaskExtended, sort.column)
        fn = None
        direction = SortDirection.from_str(sort.direction)
        if direction == SortDirection.ASC:
            fn = asc(field)
        else:
            fn = desc(field)
        stmt = stmt.order_by(fn)

    for search in searchs:
        field = getattr(TaskExtended, search.column)
        term = search.term
        stmt = stmt.where(field.like(f"%{term}%"))

    stmt = stmt.order_by(asc(TaskExtended.id))  # XXX: important
    return stmt

def clone_and_send_task(id: str):
    ar = AsyncResult(id)

    task_id = ar.task_id
    name = ar.name
    args = ar.args
    kwargs = ar.kwargs
    queue = ar.queue

    assert (
        name is not None or queue is None
    ), f"Aucun nom de tâche pour l'id {task_id}. Voir l'option 'result_extended' de celery."

    t = celeryapp.send_task(
        name,
        args=args,
        kwargs=kwargs,
        queue=queue,
    )
    logger.info(f"Tâche {task_id} cloné et envoyé, nouvelle tâche: {t.task_id}")
