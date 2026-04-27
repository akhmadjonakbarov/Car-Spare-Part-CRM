import re

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, validates

from apps.base.models import Base


class User(Base):
    __tablename__ = 'users'

    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    is_active = Column(Boolean, default=True)
    email = Column(String(length=100), unique=True)
    password = Column(String, nullable=False)

    # relationships
    employees = relationship('Employee', back_populates='user')
    purchases = relationship('Purchase', back_populates='user')
    items = relationship('Item', back_populates='user')
    currencies = relationship('Currency', back_populates='user')
    documents = relationship('Document', back_populates='user')
    document_items = relationship('DocumentItem', back_populates='user')
    document_item_balances = relationship('DocumentItemBalance', back_populates='user')
    customers = relationship('Customer', back_populates='user')
    roles = relationship('Role', secondary="users_roles", back_populates='users')

    @validates('phone_number', 'phone_number2')
    def validate_phone_number(self, key, value):
        if value and not re.match(r'^\+?\d{9,15}$', value):
            raise ValueError('Invalid phone number format. Expected format: 901234567.')
        return value
