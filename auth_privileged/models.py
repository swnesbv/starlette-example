
from __future__ import annotations

from sqlalchemy import String, Integer

from sqlalchemy.orm import Mapped, mapped_column

from db_config.storage_config import Base, intpk


class Privileged(Base):
    __tablename__ = "privileged"

    id: Mapped[intpk]
    prv_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    prv_in: Mapped[int] = mapped_column(Integer, nullable=True)

    # ...
    def __str__(self):
        return str(self.prv_key)
