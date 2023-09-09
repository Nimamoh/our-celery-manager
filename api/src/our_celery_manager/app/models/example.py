from ..models import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

# TODO: replace
class Example(Base):

    __tablename__ = "example"
    __table_args__ = { "schema": "ocm" }

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str] = mapped_column(String(30))