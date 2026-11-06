from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id_market: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    cdi: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    voltage_level: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    G: Mapped[float] = mapped_column(Float)
    T: Mapped[float] = mapped_column(Float)
    D: Mapped[float] = mapped_column(Float)
    R: Mapped[float] = mapped_column(Float)
    C: Mapped[float] = mapped_column(Float)
    P: Mapped[float] = mapped_column(Float)
    CU: Mapped[float] = mapped_column(Float)

    services: Mapped[list["Service"]] = relationship(back_populates="tariff")