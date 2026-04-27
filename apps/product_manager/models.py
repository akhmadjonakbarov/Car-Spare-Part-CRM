from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.base.models import Base


class BaseName(Base):
    __abstract__ = True
    name = Column(String(100), unique=True)

    def __str__(self):
        return self.name


class Company(BaseName):
    __tablename__ = 'companies'
    items = relationship('Item', back_populates='company')
    computers = relationship('Computer', back_populates='company')


class Category(BaseName):
    __tablename__ = 'categories'

    # relationships
    items = relationship('Item', back_populates='category')
    computers = relationship('Computer', back_populates='category')


class Unit(Base):
    __tablename__ = 'units'
    value = Column(String(25), unique=True, nullable=False)

    # relationships
    items = relationship('Item', back_populates='unit')


#
# class Item(BaseName):
#     __tablename__ = 'items'
#     barcode = Column(String(100), nullable=False, unique=True)
#     # price
#     income_price = Column(Float(), default=0.0)
#     sale_price = Column(Float(), default=0.0)
#     currency_type = Column(String(), default="uzs")
#     # categories relationships
#     category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
#     category = relationship('Category', back_populates='items')
#     # unit relationships
#     unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
#     unit = relationship('Unit', back_populates='items')
#     # company relationships
#     company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
#     company = relationship('Company', back_populates='items')
#
#     # type relationships
#     types = relationship('Type', secondary='type_item', back_populates='items')
#
#     # user relationships
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='items')
#
#     # document item relationships
#     document_items = relationship('DocumentItem', back_populates='item')
#     document_item_balances = relationship(
#         'DocumentItemBalance', back_populates='item')
#
#     # note
#     note = relationship("Note", back_populates="item", uselist=False)
#
#
# class Type(BaseName):
#     __tablename__ = 'types'
#     items = relationship('Item', secondary='type_item', back_populates='types')
#
#
# # Association Table (no model class)
# # type_item_table = Table(
# #     'type_item', Base.metadata,
# #     Column('item_id', ForeignKey('items.id'), primary_key=True),
# #     Column('type_id', ForeignKey('types.id'), primary_key=True)
# # )
#
#
# class TypeItem(Base):
#     __tablename__ = 'type_items'
#     type_id = Column(Integer, ForeignKey('types.id'), primary_key=True)
#     item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)


class Item(BaseName):
    __tablename__ = 'items'

    # Use mapped_column for better type hinting
    barcode: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    income_price: Mapped[float] = mapped_column(Float, default=0.0)
    sale_price: Mapped[float] = mapped_column(Float, default=0.0)
    currency_type: Mapped[str] = mapped_column(String, default="uzs")

    # Foreign Keys
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id'))
    unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey('units.id'))
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey('companies.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    # Relationships - Mapped[List[...]] tells your IDE exactly what to expect
    category: Mapped["Category"] = relationship(back_populates="items")
    unit: Mapped["Unit"] = relationship(back_populates="items")
    company: Mapped["Company"] = relationship(back_populates="items")
    user: Mapped["User"] = relationship(back_populates="items")

    # Many-to-Many Relationship
    # Note: Use the association table name 'type_items' defined below
    types: Mapped[List["Type"]] = relationship(
        secondary='type_items',
        back_populates='items',
        lazy="selectin"  # Recommended for async to avoid lazy load errors
    )

    document_items: Mapped[List["DocumentItem"]] = relationship(back_populates="item")
    document_item_balances: Mapped[List["DocumentItemBalance"]] = relationship(back_populates="item")
    note: Mapped[Optional["Note"]] = relationship(back_populates="item", uselist=False)


class Type(BaseName):
    __tablename__ = 'types'

    items: Mapped[List["Item"]] = relationship(
        secondary='type_items',
        back_populates='types'
    )


class TypeItem(Base):
    """Association table for Many-to-Many relationship between Type and Item"""
    __tablename__ = 'type_items'

    type_id: Mapped[int] = mapped_column(ForeignKey('types.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), primary_key=True)
