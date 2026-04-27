from sqladmin import ModelView
from .models import Document, DocumentItem, DocumentItemBalance


class DocumentAdmin(ModelView, model=Document):
    column_list = [Document.id, Document.doc_type, Document.discount, Document.user_id]
    column_searchable_list = [Document.doc_type]
    name = "Document"
    icon = "fa-solid fa-file"


class DocumentItemAdmin(ModelView, model=DocumentItem):
    column_list = [
        DocumentItem.id,
        DocumentItem.qty,
        DocumentItem.income_price,
        DocumentItem.sale_price,
        DocumentItem.item_id,
        DocumentItem.document_id,
    ]
    name = "Document Item"
    icon = "fa-solid fa-list"


class DocumentItemBalanceAdmin(ModelView, model=DocumentItemBalance):
    column_list = [
        DocumentItemBalance.id,
        DocumentItemBalance.qty,
        DocumentItemBalance.income_price,
        DocumentItemBalance.sale_price,
        DocumentItemBalance.item_id,
        DocumentItemBalance.document_id,
    ]
    name = "Document Item Balance"
    icon = "fa-solid fa-balance-scale"
