from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.record import Record


class Consumption(Base):
    __tablename__ = "consumption"

    __table_args__ = (
        CheckConstraint("value >= 0", name="ck_consumption_value_nonnegative"),
    )

    id_record: Mapped[int] = mapped_column(
        ForeignKey("records.id_record"), primary_key=True, autoincrement=False
    )
    value: Mapped[Decimal] = mapped_column(Numeric(18, 6))

    record: Mapped["Record"] = relationship(back_populates="consumption")