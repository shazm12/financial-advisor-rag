from enum import Enum
from pydantic import BaseModel


class QueryRequest(BaseModel):
    prompt: str