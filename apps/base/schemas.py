from datetime import datetime

from marshmallow import Schema, fields
from pydantic import BaseModel


class BaseSchema(Schema):
    id = fields.Int()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class BaseModelSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
