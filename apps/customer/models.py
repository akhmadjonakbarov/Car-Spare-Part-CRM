from apps.base.models import Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship, validates
import re


class Customer(Base):
    __tablename__ = 'customers'  # Specify the database table name

    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(9), nullable=False, unique=True, index=True)
    phone_number2 = Column(String(9), nullable=True, unique=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationship to UserModel
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='customers')

    # One customer has many purchases
    purchases = relationship('Purchase', back_populates='customer')
    payment_histories = relationship('PaymentHistory', back_populates='customer')
    transactions = relationship('Transaction', back_populates='customer')

    @validates('phone_number', 'phone_number2')
    def validate_phone_number(self, key, value):
        if value and not re.match(r'^\+?\d{9,15}$', value):
            raise ValueError(
                'Invalid phone number format. Expected format: 901234567.')
        return value


class PaymentHistory(Base):
    __tablename__ = 'payment_histories'
    amount = Column(Numeric())
    note = Column(String(length=400), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship('Customer', back_populates='payment_histories')
