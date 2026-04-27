from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship, mapped_column, Mapped
from apps.base.models import Base


class Purchase(Base):
    __tablename__ = 'purchases'

    user = relationship('User', back_populates='purchases')
    user_id = Column(Integer, ForeignKey('users.id'))

    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    customer = relationship('Customer', back_populates='purchases')

    document_id = Column(Integer, ForeignKey(
        'documents.id'), nullable=True, unique=True)
    document = relationship('Document', back_populates='purchase')

    is_debt = mapped_column(Boolean, nullable=False, default=False)
    paid_date = mapped_column(DateTime, nullable=True, default=None)
    total_price = mapped_column(Numeric(15, 3), default=0.0, nullable=True)
    remain_money = mapped_column(Numeric(15, 3), default=0.0, nullable=True)
    paid_money: Mapped[Numeric] = mapped_column(Numeric(15, 3), nullable=True, default=0.0)

    transactions = relationship(
        "Transaction",
        back_populates="purchase",
        cascade="all, delete-orphan",  # optional but common
        passive_deletes=True
    )

    def pay(self):
        if not self.is_debt:
            raise ValueError("This purchase is already paid")
        self.is_debt = False
        self.paid_date = Base.tashkent_now()
        self.remain_money = 0.0

    def __str__(self):
        return f"{self.customer.full_name} {self.remain_money} debt:{self.is_debt} paid:{self.paid_date}"
