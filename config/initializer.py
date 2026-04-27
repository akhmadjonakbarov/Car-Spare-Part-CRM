from sqlalchemy.orm import Session
from apps.role_manager.models import SalaryType, Role, UsersRoles, Employee
from apps.user.models import User
from apps.initializer.models import Initializer as InitializerModel
from apps.product_manager.models import Unit
from config.security import get_password_hash
from sqlalchemy.orm import Session


class Initializer:
    def __init__(self, db: Session):
        self.db = db

    def initialize(self):
        try:
            is_initialized = self.db.query(InitializerModel).first()
            if is_initialized is None:
                print("[+] Initializing database...\n")
                self.insert_units()
                self.create_admin()
                # self.insert_currency()
                self.db.add(InitializerModel(value=True))
                self.db.commit()
                print("[✓] Initialization completed.\n")

        except Exception as e:
            print(f"[✗] Initialization error: {e}")
            self.db.rollback()

    def insert_units(self):
        print("[+] Inserting measurement units...\n")
        units = ['kg', 'dona', 'metr']
        for unit in units:
            self.db.add(Unit(value=unit))

    def insert_currency(self):
        from apps.currency.models import Currency
        self.db.add(Currency(
            value=12500
        ))

    def create_admin(self):
        print("[+] Creating admin user...\n")

        # 1. Foydalanuvchi
        created_user = User(
            email="akhmad@gmail.com",
            first_name="Akhmad",
            last_name="Akbarov",
            password=get_password_hash("admin123")
        )
        self.db.add(created_user)
        self.db.flush()  # ID olish uchun

        # 2. Maosh turi
        salary_type = SalaryType()
        self.db.add(salary_type)
        self.db.flush()

        # 3. Rol
        role = Role(
            name="admin",
            user_id=created_user.id
        )
        self.db.add(role)
        self.db.flush()

        # 4. Xodim
        employee = Employee(
            role_id=role.id,
            base_salary=12_000_000,
            salary_type_id=salary_type.id,
            user_id=created_user.id
        )
        self.db.add(employee)
        self.db.flush()

        # 5. Rol biriktirish
        user_role = UsersRoles(
            user_id=created_user.id,
            role_id=role.id
        )
        self.db.add(user_role)
        self.db.flush()
