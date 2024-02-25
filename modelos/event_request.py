from pydantic import BaseModel

class EventResponse(BaseModel):
    event: str
    body: dict
    id: str
    headers:dict
    status_code: int
    