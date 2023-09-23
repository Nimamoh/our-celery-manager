from typing import Dict, Tuple
from our_celery_manager.app.models.dtos.tasks import ListResultRow
from our_celery_manager.app.service.ocm_taskmeta import OcmTaskMetaService
from . import logger

from sqlalchemy.orm import Session

from our_celery_manager.app.service.celery.model import SearchField, SortDirection, SortField
from our_celery_manager.app.models.ocm.clone import CloneEvent
from celery.backends.database.models import TaskExtended


from our_celery_manager.app.models.dtos.tasks import TaskResult as TaskResultDto, ListResultRow, ListResult

from sqlalchemy import Select, asc, desc, join, select, func, String
from sqlalchemy.orm import aliased

from celery.result import AsyncResult

from our_celery_manager.app.tasks_queue import app as celeryapp

TaskIdTable = Tuple[str, str, str]

def _tasks(
    sorts: list[SortField],
    searchs: list[SearchField],
) -> Select[TaskIdTable]:


    select_fields = TaskResultDto.fields_to_select(TaskExtended)
    stmt = select(
        TaskExtended.task_id.label("clone").cast(String),
        TaskExtended.task_id.label("src").cast(String),
        TaskExtended.task_id.label("root").cast(String),
        *select_fields
    ) \
        .select_from(join(TaskExtended, CloneEvent, CloneEvent.clone_id == TaskExtended.task_id, isouter=True)) \
        .where(CloneEvent.id.is_(None))

    # Apply sorts
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

    stmt = stmt.order_by(asc(TaskExtended.id)) # XXX: important
    return stmt

def _tasks_with_clones(tasks: Select[TaskIdTable]):
    """
    Lists table of tasks id:
    | clone | src | root |
    clone: being the clone tasks, which have src
    root being the original task id in cast of transitive clones
    """

    subq = tasks.subquery()
    root_tasks = select(
        subq.c.task_id.label("clone").cast(String),
        subq.c.task_id.label("src").cast(String),
        subq.c.task_id.label("root").cast(String),
    ).select_from(subq)

    cte = root_tasks \
        .cte("cte", recursive=True)

    clones = select(
        CloneEvent.clone_id.label('clone').cast(String),
        CloneEvent.task_id.label('src').cast(String),
        cte.c.root.label('root').cast(String),
    ) \
        .select_from(join(CloneEvent, cte, CloneEvent.task_id == cte.c.clone)) \

    root_with_clones = root_tasks.union_all(clones)
    return root_with_clones

def result_page(
        pageSize: int,
        pageNumber: int,
        sorts: list[SortField],
        searchs: list[SearchField],
        session: Session
    ) -> ListResult:
    tasks = _tasks(sorts, searchs)

    total = session.query(func.count()).select_from(tasks.subquery()).scalar()

    limit = pageSize
    offset = pageNumber*pageSize
    tasks = tasks.limit(limit)
    tasks = tasks.offset(offset)

    tasks_with_clones = _tasks_with_clones(tasks)

    a_root = aliased(TaskExtended)
    a_clone = aliased(TaskExtended)

    a_root_fields = ListResultRow.fields_to_select(a_root)
    a_clone_fields = ListResultRow.fields_to_select(a_clone)

    q = select(
        *a_root_fields,
        *a_clone_fields,
        tasks_with_clones.c.clone, 
        tasks_with_clones.c.src, 
        tasks_with_clones.c.root, 
    ) \
        .select_from(tasks_with_clones) \
            .join(a_clone, a_clone.task_id == tasks_with_clones.c.clone, isouter=True) \
            .join(a_root, a_root.task_id == tasks_with_clones.c.root, isouter=True) \

    q_result = session.execute(q)

    task_index: Dict[str, ListResultRow] = {}

    # Construct the DTOs
    result_rows: list[ListResultRow] = []
    for row in q_result:
        root_args = list(row[0:len(a_root_fields)])
        root_args.append([])

        offset = len(a_root_fields)

        clone_args = list(row[offset:offset + len(a_clone_fields)])
        clone_args.append([])

        offset += len(a_clone_fields)

        clone_tbl_args = row[offset:offset + 3]

        try:
            root = ListResultRow.from_list(root_args)
            clone = ListResultRow.from_list(clone_args)
        except Exception:
            logger.warning("Impossible to retrieve task from result backend. Skipping.")
            continue

        (clone_taskid, src_taskid, root_taskid) = clone_tbl_args

        if clone_taskid == root_taskid: # Task is a root without a clone
            task_index[root_taskid] = root
            result_rows.append(root)
            continue

        indexed_root = task_index[root_taskid]
        indexed_root.clones.append(clone)

    result = ListResult(total = total, page_number=pageNumber, page_size=pageSize, data=result_rows)
    return result

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
