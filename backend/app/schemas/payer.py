from typing import Optional

from pydantic import BaseModel


class PayerResponse(BaseModel):
    id: int
    name: str
    plan_name: Optional[str] = None

    model_config = {"from_attributes": True}
