from pydantic import BaseModel
from typing import Optional


class ActionBase(BaseModel):
    name: str
    status: bool
    fixed_name: str


class ActionRead(ActionBase):
    pass


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    name: Optional[str]
    status: Optional[bool]
    fixed_name: Optional[str]
