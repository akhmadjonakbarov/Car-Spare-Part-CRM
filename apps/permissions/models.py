from sqlalchemy import ForeignKey, Integer, Column
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Permission(Base):
    __tablename__ = 'permissions'
    role_id = Column(Integer, ForeignKey('roles.id'))
    action_id = Column(Integer, ForeignKey('actions.id'))

    role = relationship("Role", back_populates="permissions")
    action = relationship("Action", back_populates="permissions")
