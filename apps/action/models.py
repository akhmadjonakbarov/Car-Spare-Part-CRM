from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Action(Base):
    __tablename__ = 'actions'
    name = Column(String, unique=True)
    status = Column(Boolean, nullable=False, default=False)
    fixed_name = Column(String, unique=True)

    permissions = relationship("Permission", back_populates="action")

    def __str__(self):
        return self.name
