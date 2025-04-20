from pydantic import BaseModel
from datetime import date
from typing import List

class CotizacionBase(BaseModel):
    fecha: date
    valor: float

class CotizacionCreate(CotizacionBase):
    pass

class Cotizacion(CotizacionBase):
    id: int

    class Config:
        from_attributes = True

class CotizacionResponse(BaseModel):
    fecha: str
    valor: float 