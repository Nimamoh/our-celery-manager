import pytz
from our_celery_manager.app.models.task.TaskResult import TaskResult, Status
from our_celery_manager.app.service.celery.model import DbResultRow

_utc = pytz.timezone('UTC')

def map_result(row: DbResultRow) -> TaskResult:

    tr_result = str(row.result)
    tr_status = Status(row.status)

    # XXX: apparently, date_done is stored in base without tz info, restore the correct tz
    tr_date_done = _utc.localize(row.date_done) if row.date_done is not None else None

    return TaskResult(
        row.id,
        row.name,
        tr_status,
        tr_date_done,
        traceback=row.traceback,
        queue=row.queue,
        args=row.args,
        kwargs=row.kwargs,
        result=tr_result,
    )
