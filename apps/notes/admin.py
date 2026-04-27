from sqladmin import ModelView
from .models import Note


class NoteAdmin(ModelView, model=Note):
    column_list = [Note.id, Note.item_id]
    name = "Note"
    icon = "fa-solid fa-sticky-note"
