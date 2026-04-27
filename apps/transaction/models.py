from sqlalchemy import Numeric, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship('Customer', back_populates='transactions')
    amount = Column(Numeric(15, 3))

    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    purchase = relationship("Purchase", back_populates="transactions")
