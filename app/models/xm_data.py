from datetime import datetime

from sqlalchemy import DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class XMDataHourlyPerAgent(Base):
    __tablename__ = "xm_data_hourly_per_agent"

    record_timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    value: Mapped[float] = mapped_column(Float)

    records: Mapped[list["Record"]] = relationship(back_populates="xm_data")