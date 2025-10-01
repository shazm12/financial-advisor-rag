from enum import Enum
from pydantic import BaseModel


class QueryRequest(BaseModel):
    session_id: str
    prompt: str