from typing import Literal
from pydantic import BaseModel


class AnalystResponse(BaseModel):
    kind: Literal["sql", "clarification", "unsupported"]
    sql: str
    message: str
