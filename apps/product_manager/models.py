from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.base.models import Base
from apps.company.models import Company


class BaseName(Base):
    __abstract__ = True
    name = Column(String(100))

    def __str__(self):
        return self.name


class Car(BaseName):
    __tablename__ = 'cars'
    items = relationship('Item', back_populates='car')


class Category(BaseName):
    __tablename__ = 'categories'

    # relationships
    items = relationship('Item', back_populates='category')


class Unit(Base):
    __tablename__ = 'units'
    value = Column(String(25), unique=True, nullable=False)

    # relationships
    items = relationship('Item', back_populates='unit')

    def __str__(self):
        return self.value


class Item(BaseName):
    __tablename__ = 'items'

    # Use mapped_column for better type hinting
    barcode: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
    income_price: Mapped[float] = mapped_column(Float, default=0.0)
    sale_price: Mapped[float] = mapped_column(Float, default=0.0)
    currency_type: Mapped[str] = mapped_column(String, default="uzs")

    # Foreign Keys
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('categories.id'))
    unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey('units.id'))

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    car_id: Mapped[int] = mapped_column(
        ForeignKey('cars.id'), nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('companies.id'))

    # Relationships - Mapped[List[...]] tells your IDE exactly what to expect
    category: Mapped["Category"] = relationship(back_populates="items")
    unit: Mapped["Unit"] = relationship(back_populates="items")
    user: Mapped["User"] = relationship(back_populates="items")
    car: Mapped["Car"] = relationship(
        back_populates="items",
    )
    company: Mapped[Optional["Company"]] = relationship(back_populates="items")

    # Many-to-Many Relationship
    # Note: Use the association table name 'type_items' defined below
    types: Mapped[List["Type"]] = relationship(
        secondary='type_items',
        back_populates='items',
        lazy="selectin"  # Recommended for async to avoid lazy load errors
    )

    document_items: Mapped[List["DocumentItem"]
                           ] = relationship(back_populates="item")
    document_item_balances: Mapped[List["DocumentItemBalance"]] = relationship(
        back_populates="item")
    note: Mapped[Optional["Note"]] = relationship(
        back_populates="item", uselist=False)


class Type(BaseName):
    __tablename__ = 'types'

    items: Mapped[List["Item"]] = relationship(
        secondary='type_items',
        back_populates='types'
    )


class TypeItem(Base):
    """Association table for Many-to-Many relationship between Type and Item"""
    __tablename__ = 'type_items'

    type_id: Mapped[int] = mapped_column(
        ForeignKey('types.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey('items.id'), primary_key=True)
