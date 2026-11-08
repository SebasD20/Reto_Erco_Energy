from decimal import Decimal

from pydantic import BaseModel


class ClientStatisticsResponse(BaseModel):
    service_id: int
    year: int | None
    month: int | None

    cantidad_mediciones: int

    consumo_total_kwh: Decimal
    inyeccion_total_kwh: Decimal
    balance_kwh: Decimal

    consumo_promedio_kwh: Decimal
    inyeccion_promedio_kwh: Decimal

    consumo_maximo_kwh: Decimal
    inyeccion_maxima_kwh: Decimal
