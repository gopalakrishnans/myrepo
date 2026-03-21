from typing import Optional

from pydantic import BaseModel


class ProcedureResponse(BaseModel):
    id: int
    billing_code: str
    code_type: str
    description: Optional[str] = None
    plain_language_name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}
