import os
import random

from app.models import User, Employee, Shop, Food
from app import db, config
from faker import Factory

fk = Factory.create()
MIN_SALARY = 1300
MAX_SALARY = 3000

MIN_PRICE = 3
MAX_PRICE = 50

RATE_EXTRA = 0.1

def create_default_admin():
    admin_email = config['ADMIN_EMAIL']
    admin_password = config['ADMIN_PASSWORD']
    admin = User(email=admin_email, password=admin_password, confirmed=True, is_admin=True, is_manager=True)
    db.session.add(admin)
    db.session.commit()
    admin_employee = Employee(firstname='Vincent', lastname='Houba', salary=2000, user=admin)
    db.session.add(admin_employee)
    db.session.commit()

    
def create_default_shop():
    shop_email = config['DEFAULT_SHOP_EMAIL']
    shop = Shop(name='shop', email=shop_email, telephone='0499316385', address='rue machin 4311 liege') 
    db.session.add(shop)
    db.session.commit()

    
def create_managers(count=10):
    for _ in range(count):
        email = fk.email()
        password = fk.password()
        confirmed = True
        is_manager = True
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def create_employees(count=50, manager=False):
    for _ in range(count):
        email = fk.email()
        password = fk.password()
        confirmed = True
        firstname = fk.first_name()
        lastname = fk.last_name()
        salary = random.randint(MIN_SALARY, MAX_SALARY)
        user = User(email=email, password=password, confirmed=True, is_manager=manager)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        employee = Employee(user=user, firstname=firstname, lastname=lastname, salary=salary)
        db.session.add(employee)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()



def create_shops(count=5):
    for _ in range(count):
        name = fk.company()
        email = fk.email()
        telephone = fk.phone_number()
        address = fk.street_address ()
        shop = Shop(name=name, email=email, telephone=telephone, address=address)
        db.session.add(shop)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()



def create_foods(count=200):
    shops = Shop.query.all()
    rate_extra = 0.1
    for _ in range(count):
        name = fk.name()
        price = (random.random() * MAX_PRICE) + MAX_PRICE
        extra = True if RATE_EXTRA <= random.random() else False
        shop = random.choice(shops)
        food = Food(name=name, price=price, extra=extra, shop=shop)
        db.session.add(food)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def create_commands(waiting_count=1, done_count=3, cancel_count=2):
    managers = User.query.filter_by(is_manager=True)
    delivery_address = config['COMPANY_ADDRESS']
    
    
