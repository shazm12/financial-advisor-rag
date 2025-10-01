from enum import Enum
from typing import Optional
from pydantic import BaseModel

class Status(str, Enum):
    SUCCESS="success"
    FAILURE="fail"


class ExtractionResponse(BaseModel):
    status: Status
    session_id: str
    description: Optional[str] = None
    
class QueryResponse(BaseModel):
    status: Status
    response: str
    description: Optional[str] = None
    session_id: str