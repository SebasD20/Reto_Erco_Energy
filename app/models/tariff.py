from decimal import Decimal
from sqlalchemy import Numeric, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Tariff(Base):
    __tablename__ = "tariffs"
    __table_args__ = (
        Index(
            "uq_tariffs_market_voltage_cdi",
            "id_market",
            "voltage_level",
            "cdi",
            unique=True,
            postgresql_where=text("cdi IS NOT NULL"),
        ),
        Index(
            "uq_tariffs_market_voltage_no_cdi",
            "id_market",
            "voltage_level",
            unique=True,
            postgresql_where=text("cdi IS NULL"),
        ),
    )

    id_tariff: Mapped[int] = mapped_column(primary_key=True)
    id_market: Mapped[int] = mapped_column()
    cdi: Mapped[int | None] = mapped_column(nullable=True)
    voltage_level: Mapped[int] = mapped_column()
    G: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    T: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    D: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    R: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    C: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    P: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    CU: Mapped[Decimal] = mapped_column(Numeric(18, 8))
