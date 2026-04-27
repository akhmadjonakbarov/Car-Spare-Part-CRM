from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column

from apps.base.models import Base


class Currency(Base):
    __tablename__ = 'currencies'  # Specify the database table name

    value: Mapped[float] = Column(Numeric(15, 3), default=0.0, nullable=True)
    # Relationship to CustomUserModel
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.id'), nullable=False)  # ForeignKey to CustomUserModel
    user = relationship('User', back_populates='currencies')

    # Relationship to DocumentItemBalanceModel
    document_items = relationship('DocumentItem', back_populates='currency')
    document_item_balances = relationship('DocumentItemBalance', back_populates='currency')

    def __str__(self):
        return self.value

    def __repr__(self):
        return (f"<Currency("
                f"value={self.value}, "
                f"id={self.id},) > ")
