from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from celery.backends.database.models import TaskExtended
from our_celery_manager.app.models.ocm.clone import CloneEvent

from sqlalchemy.orm import aliased
from sqlalchemy import func

#region: service layer
@dataclass
class SearchField:
    column: str
    term: str

    @staticmethod
    def from_api_str(s: str):
        split = s.split(":", 1)
        assert len(split) == 2, f"'{s}' != 'col: term'"
        col = split[0].strip()
        term = split[1].strip()
        return SearchField(col, term)


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == SortDirection.ASC:
            return SortDirection.ASC
        else:
            return SortDirection.DESC

@dataclass
class SortField:
    column: str
    direction: SortDirection

    @staticmethod
    def from_api_str(s: str):
        split = s.split(" ")
        assert len(split) == 2, f"'{s}' != 'column [ASC|DESC]'"
        col = split[0]
        dir: SortDirection = split[1]  # type: ignore

        return SortField(col, dir)
#endregion

# region: db layer
@dataclass
class DbResultRow:
    """Structure d'une ligne (voir db_result_select_fields)"""
    id: str
    name: str | None
    status: str
    date_done: datetime | None
    traceback: str | None
    queue: str | None

    args: bytes | None
    kwargs: bytes | None

    result: object

    nb_clones: int

"""Liste des champs de selection pour la table des taches"""
cloned = aliased(CloneEvent)
being_a_clone = aliased(CloneEvent)
db_result_select_fields =  (
    TaskExtended.task_id,
    TaskExtended.name,
    TaskExtended.status,
    TaskExtended.date_done,
    TaskExtended.traceback,
    TaskExtended.queue,
    TaskExtended.args,
    TaskExtended.kwargs,
    TaskExtended.result,
    func.count(cloned.id),
)
# endregion