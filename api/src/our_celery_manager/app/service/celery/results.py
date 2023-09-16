from dataclasses import dataclass
from our_celery_manager.app.service.ocm_taskmeta import OcmTaskMetaService
from . import logger

from sqlalchemy.orm import Session

from our_celery_manager.app.service.celery.model import DbResultRow, SearchField, SortDirection, SortField, db_result_select_fields, cloned, being_a_clone
from our_celery_manager.app.service.celery.mapper import map_result
from our_celery_manager.app.models.ocm.clone import CloneEvent
from celery.backends.database.models import TaskExtended

from our_celery_manager.app.models.task.TaskResult import TaskResult, TaskResultPage

from sqlalchemy import asc, desc, join, select, func, text, union_all, String
from sqlalchemy.orm import aliased, with_expression

from celery.result import AsyncResult

from our_celery_manager.app.tasks_queue import app as celeryapp

@dataclass
class RowExp:
    task_id: str
    nb_clones: int

def result_page_exp(session: Session) -> list[RowExp]:
    te1 = aliased(TaskExtended)
    te2 = aliased(TaskExtended)
    ce = aliased(CloneEvent)

    # root tasks (those not cloned)
    q_root_tasks = select(
        te1.task_id.label("clone").cast(String),
        te1.task_id.label("src").cast(String),
        te1.task_id.label("racine").cast(String),
        # text("'racine'"),
    ) \
        .select_from(join(te1, ce, ce.clone_id == te1.task_id, isouter=True)) \
        .where(ce.id.is_(None)) \
        .order_by(te1.date_done, te1.id) \
        .limit(100) \
        .offset(0)

    root_tasks = q_root_tasks \
        .cte("cte", recursive=True)
    
    # clones
    clones = select(
        ce.clone_id.label('clone').cast(String),
        ce.task_id.label('src').cast(String),
        root_tasks.c.racine.label('racine').cast(String),
        # text("'clone'"),
    ) \
    .select_from(join(ce, root_tasks, ce.task_id == root_tasks.c.clone))

    union_root_clones = root_tasks.union_all(clones)

    a_racine = aliased(TaskExtended)
    a_clone = aliased(TaskExtended)
    q = select(union_root_clones.c.racine, func.count(union_root_clones.c.clone) - 1) \
        .select_from(union_root_clones) \
            .join(a_clone, a_clone.task_id == union_root_clones.c.clone, isouter=True) \
            .join(a_racine, a_racine.task_id == union_root_clones.c.racine, isouter=True) \
            .group_by(union_root_clones.c.racine)

    result = session.execute(q)
    # result = session.execute(q_root_tasks)
    # result = session.execute(select("*").select_from(union_root_clones))

    r = []
    for row in result:
        r.append(RowExp(row[0], row[1]))

    return r

def result_page(
    pageSize: int,
    pageNumber: int,
    sorts: list[SortField],
    searchs: list[SearchField],
    session: Session
) -> TaskResultPage:
    assert pageSize < 100, "La taille de la page doit être <100"
    assert pageNumber >= 0, "Le numéro de page doit être positif"

    stmt = _stmt(sorts, searchs)
    paginated_stmt = stmt.limit(pageSize).offset((pageNumber)*pageSize)

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

    # We sort out the source of cloned tasks since only last ones interest us
    # TODO: is it really what we want?!
    stmt = stmt.outerjoin(cloned, cloned.task_id == TaskExtended.task_id)
    stmt = stmt.outerjoin(being_a_clone, being_a_clone.clone_id == TaskExtended.task_id)
    stmt = stmt.filter(being_a_clone.id == None)
    stmt = stmt.group_by(TaskExtended.id)

    stmt = stmt.order_by(asc(TaskExtended.id))  # XXX: important
    return stmt

def clone_and_send_task(id: str, session: Session):
    ar = AsyncResult(id)

    task_id = ar.task_id
    name = ar.name
    args = ar.args
    kwargs = ar.kwargs
    queue = ar.queue

    assert (
        name is not None or queue is None
    ), f"Aucun nom de tâche pour l'id {task_id}. Voir l'option 'result_extended' de celery."

    t: AsyncResult = celeryapp.send_task(
        name,
        args=args,
        kwargs=kwargs,
        queue=queue,
    )

    OcmTaskMetaService.make(session).record_cloned(task_id, t.task_id)
    logger.info(f"Tâche {task_id} cloné et envoyé, nouvelle tâche: {t.task_id}")
