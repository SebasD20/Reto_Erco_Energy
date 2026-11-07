from typing import TYPE_CHECKING

from sqlalchemy import and_, or_
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.db import Base
from app.models.tariff import Tariff

if TYPE_CHECKING:
    from app.models.record import Record


class Service(Base):
    __tablename__ = "services"

    id_service: Mapped[int] = mapped_column(primary_key=True)
    id_market: Mapped[int] = mapped_column()
    cdi: Mapped[int] = mapped_column()
    voltage_level: Mapped[int] = mapped_column()

    tariff: Mapped["Tariff | None"] = relationship(
        primaryjoin=lambda: and_(
            foreign(Service.id_market) == Tariff.id_market,
            foreign(Service.voltage_level) == Tariff.voltage_level,
            or_(
                and_(Service.voltage_level == 1, foreign(Service.cdi) == Tariff.cdi),
                and_(Service.voltage_level.in_([2, 3]), Tariff.cdi.is_(None)),
            ),
        ),
        viewonly=True,
        uselist=False,
    )
    records: Mapped[list["Record"]] = relationship(back_populates="service")