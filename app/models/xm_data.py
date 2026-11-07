from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.record import Record


class XMDataHourlyPerAgent(Base):
    __tablename__ = "xm_data_hourly_per_agent"

    record_timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 10))

    records: Mapped[list["Record"]] = relationship(back_populates="xm_data")