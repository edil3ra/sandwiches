import os
from app.models import User, Employee
from app import db
from faker import Factory
import random

fk = Factory.create()
MIN_SALARY = 1300
MAX_SALARY = 3000


def create_admin():
    email = os.environ.get('ADMIN_EMAIL') or 'admin'
    password = os.environ.get('ADMIN_PASSWORD') or 'admin'
    user = User(email=email, password=password, confirmed=True, is_admin=True)
    db.session.add(user)
    db.session.commit()

    
def create_managers(count=10):
    for _ in range(count):
        email = fk.email()
        password = fk.password()
        confirmed = True
        is_manager = True
        db.session.add(user)
        db.session.commit()


def create_employees(count=50, manager=False):
    for _ in range(count):
        email = fk.email()
        password = fk.password()
        confirmed = True
        name = fk.first_name()
        salary = random.randint(MIN_SALARY, MAX_SALARY)
        user = User(email=email, password=password, confirmed=True, is_manager=manager)
        db.session.add(user)
        db.session.commit()
        employee = Employee(user=user, name=name, salary=salary)
        db.session.add(employee)

