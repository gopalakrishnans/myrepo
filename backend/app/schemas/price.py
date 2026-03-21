from typing import Optional

from pydantic import BaseModel


class PriceResponse(BaseModel):
    id: int
    hospital_name: str
    hospital_city: Optional[str] = None
    hospital_state: Optional[str] = None
    procedure_name: str
    billing_code: str
    payer_name: Optional[str] = None
    plan_name: Optional[str] = None
    gross_charge: Optional[float] = None
    discounted_cash_price: Optional[float] = None
    negotiated_rate: Optional[float] = None
    min_negotiated_rate: Optional[float] = None
    max_negotiated_rate: Optional[float] = None


class PriceCompareResponse(BaseModel):
    procedure_name: str
    billing_code: str
    hospitals: list["HospitalPriceDetail"]


class HospitalPriceDetail(BaseModel):
    hospital_id: int
    hospital_name: str
    city: Optional[str] = None
    state: Optional[str] = None
    cash_price: Optional[float] = None
    gross_charge: Optional[float] = None
    payer_rates: list["PayerRate"]


class PayerRate(BaseModel):
    payer_name: str
    plan_name: Optional[str] = None
    negotiated_rate: Optional[float] = None


class ProcedureStats(BaseModel):
    procedure_id: int
    plain_language_name: str
    billing_code: str
    cash_price_avg: Optional[float] = None
    cash_price_median: Optional[float] = None
    cash_price_min: Optional[float] = None
    cash_price_max: Optional[float] = None
    cash_price_count: int = 0
    negotiated_avg: Optional[float] = None
    negotiated_min: Optional[float] = None
    negotiated_max: Optional[float] = None
    fair_price: Optional[float] = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
