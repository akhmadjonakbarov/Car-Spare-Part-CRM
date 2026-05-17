from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Company(Base):
    __tablename__ = 'companies'

    name = Column(String(200), nullable=False)
    items = relationship('Item', back_populates='company')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
