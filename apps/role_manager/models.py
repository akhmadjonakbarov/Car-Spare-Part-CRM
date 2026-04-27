from sqlalchemy import Column, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship, validates
from apps.base.models import Base


class Role(Base):
    __tablename__ = 'roles'

    _ADMIN = "admin"
    _MANAGER = "manager"
    _EMPLOYEE = "employee"
    name = Column(String, default=_ADMIN)

    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship("User", secondary="users_roles", back_populates="roles")

    permissions = relationship("Permission", back_populates="role")
    employees = relationship("Employee", back_populates="role")

    def __str__(self):
        return self.name


class UsersRoles(Base):
    __tablename__ = 'users_roles'
    user_id = Column(Integer, ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))


class SalaryType(Base):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    DAILY = "daily"
    HOURLY = "hourly"

    __tablename__ = 'salary_types'

    type_of_salary = Column(String, default=MONTHLY)
    employee = relationship('Employee', back_populates='salary_type', uselist=False)


class Employee(Base):
    __tablename__ = 'employees'
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    user = relationship('User', back_populates='employees')

    salary_type_id = Column(Integer, ForeignKey('salary_types.id'))
    salary_type = relationship('SalaryType', back_populates='employee')
    base_salary = Column(Numeric, nullable=True)

    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='employees')

    @validates('base_salary')
    def validate_base_salary(self, key, base_salary):
        if base_salary and base_salary < 0:
            raise ValueError('Invalid base salary. Base salary must be positive.')
        return base_salary
