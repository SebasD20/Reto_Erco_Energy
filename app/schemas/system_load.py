
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SystemLoadHour(BaseModel):
    """Consumo agregado en una fecha y hora."""

    fecha_hora: datetime
    consumo_total_kwh: Decimal
    cantidad_servicios: int


class SystemLoadResponse(BaseModel):
    """Respuesta paginada de carga energética."""

    year: int | None
    month: int | None

    limit: int
    offset: int
    total_horas: int

    items: list[SystemLoadHour]
