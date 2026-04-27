from marshmallow import fields
from .models import Note
from apps.base.schemas import BaseSchema


class NoteSerializer(BaseSchema):
    category = fields.Method("get_category")
    unit = fields.Method("get_unit")
    name = fields.Method("get_name")

    @classmethod
    def get_category(cls, obj: Note):
        return obj.item.category.name

    @classmethod
    def get_name(cls, obj: Note):
        return obj.item.name

    @classmethod
    def get_unit(cls, obj: Note):
        return obj.item.unit.value
