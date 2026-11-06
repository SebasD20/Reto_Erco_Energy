from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_market", "cdi", "voltage_level"],
            ["tariffs.id_market", "tariffs.cdi", "tariffs.voltage_level"],
        ),
    )

    id_service: Mapped[int] = mapped_column(primary_key=True)
    id_market: Mapped[int] = mapped_column()
    cdi: Mapped[int] = mapped_column()
    voltage_level: Mapped[int] = mapped_column()

    tariff: Mapped["Tariff"] = relationship(back_populates="services")
    records: Mapped[list["Record"]] = relationship(back_populates="service")