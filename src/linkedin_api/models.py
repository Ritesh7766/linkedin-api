from pydantic import BaseModel


class ComponentResponse(BaseModel):
    component: str
    status_code: int
    data: str
