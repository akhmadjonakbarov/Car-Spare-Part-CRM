from pydantic import BaseModel

from apps.action.schemas import ActionRead
from apps.base.schemas import BaseModelSchema


class PermissionBase(BaseModel):
    role_id: int
    action_id: int


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(BaseModelSchema):
    role: str
    action: ActionRead
