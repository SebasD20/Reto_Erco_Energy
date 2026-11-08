
from decimal import Decimal

from pydantic import BaseModel, Field

from typing import Literal


class InvoiceRequest(BaseModel):
    """Datos necesarios para calcular una factura."""

    service_id: int = Field(gt=0)
    year: int = Field(ge=1, le=9998)
    month: int = Field(ge=1, le=12)


class InvoiceConcept(BaseModel):
    """Resultado de un concepto de facturación."""

    cantidad_kwh: Decimal
    tarifa: Decimal | None
    importe: Decimal


class InvoiceResponse(BaseModel):
    """Resultado resumido de la facturación."""

    service_id: int
    year: int
    month: int

    EA: InvoiceConcept
    EC: InvoiceConcept
    EE1: InvoiceConcept
    EE2: InvoiceConcept

    subtotal_neto: Decimal


class ConceptRequest(InvoiceRequest):
    """Solicitud para calcular un concepto individual."""

    concept: Literal["EA", "EC", "EE1", "EE2"]


class ConceptResponse(BaseModel):
    """Respuesta correspondiente a un solo concepto."""

    service_id: int
    year: int
    month: int

    concept: Literal["EA", "EC", "EE1", "EE2"]
    result: InvoiceConcept
