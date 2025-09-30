from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    SUCCESS="success"
    FAILURE="fail"


class ExtractionResponse(BaseModel):
    status: Status
    description: str
    
class QueryResponse(BaseModel):
    status: Status
    response: str