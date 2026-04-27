from sqlalchemy import Column, Boolean

from apps.base.models import Base


class Initializer(Base):
    __tablename__ = "initializer"
    value = Column(Boolean, nullable=False, default=False)
