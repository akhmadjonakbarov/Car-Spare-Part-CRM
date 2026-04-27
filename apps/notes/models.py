from sqlalchemy import String, Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Note(Base):
    __tablename__ = 'notes'
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    item = relationship('Item', back_populates='note')
