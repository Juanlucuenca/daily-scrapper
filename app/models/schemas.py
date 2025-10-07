from pydantic import BaseModel
from typing import List
from datetime import date

class FinancialRecord(BaseModel):
    fecha: str
    valor: float

class FinancialDataResponse(BaseModel):
    data: List[FinancialRecord]
    total_records: int

class HealthCheckResponse(BaseModel):
    status: str
    uva_scraping: bool
    dolar_mayorista_scraping: bool
    dolar_mep_scraping: bool
    uva_value: float | None = None
    dolar_mayorista_value: float | None = None
    dolar_mep_value: float | None = None
    errors: List[str] = []
