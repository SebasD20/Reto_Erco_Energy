from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.consumption import Consumption
    from app.models.injection import Injection
    from app.models.service import Service
    from app.models.xm_data import XMDataHourlyPerAgent


class Record(Base):
    __tablename__ = "records"

    # Un servicio solo puede tener una medicion por instante.
    # PostgreSQL crea un indice unico para esta restriccion.
    __table_args__ = (
        UniqueConstraint(
            "id_service", "record_timestamp", name="uq_records_service_timestamp"
        ),
    )

    id_record: Mapped[int] = mapped_column(primary_key=True)
    id_service: Mapped[int] = mapped_column(
        ForeignKey("services.id_service"), index=True
    )
    record_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        ForeignKey("xm_data_hourly_per_agent.record_timestamp"),
        index=True,
    )

    service: Mapped["Service"] = relationship(back_populates="records")
    xm_data: Mapped["XMDataHourlyPerAgent"] = relationship(back_populates="records")
    injection: Mapped["Injection | None"] = relationship(
        back_populates="record", uselist=False
    )
    consumption: Mapped["Consumption | None"] = relationship(
        back_populates="record", uselist=False
    )