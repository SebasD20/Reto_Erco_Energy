from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Injection(Base):
    __tablename__ = "injection"

    id_record: Mapped[int] = mapped_column(
        ForeignKey("records.id_record"), primary_key=True, autoincrement=False
    )
    value: Mapped[float] = mapped_column(Float)

    record: Mapped["Record"] = relationship(back_populates="injection")