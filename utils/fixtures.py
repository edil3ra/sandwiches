import os
import random
from datetime import datetime, timedelta
from faker import Factory

from sqlalchemy.exc import IntegrityError

from app.models import User, Employee, Shop, Food, Command, Order
from app import create_app, db

MIN_SALARY = 1300
MAX_SALARY = 3000

MIN_PRICE = 3
MAX_PRICE = 50

RATE_EXTRA = 0.1

MINUTE_MIN_SENDED = 1 * 5 * 60
MINUTE_MAX_SENDED = 30 * 24 * 60

MINUTE_MIN_RECIEVED = 1 * 1 * 30
MINUTE_MAX_RECIEVED = 1 * 4 * 60

current_app = create_app('development')
config = current_app.config

fk = Factory.create()


def create_default_admin():
    admin_email = config['ADMIN_EMAIL']
    admin_password = config['ADMIN_PASSWORD']
    admin = User(
        email=admin_email,
        password=admin_password,
        confirmed=True,
        is_admin=True,
        is_manager=True)
    db.session.add(admin)
    db.session.commit()
    admin_employee = Employee(
        firstname='Vincent', lastname='Houba', salary=2000, user=admin)
    db.session.add(admin_employee)
    db.session.commit()


def create_default_shop():
    shop_email = config['DEFAULT_SHOP_EMAIL']
    shop = Shop(
        name='shop',
        email=shop_email,
        telephone='0499316385',
        address='rue machin 4311 liege')
    db.session.add(shop)
    db.session.commit()


def create_default_command():
    admin = User.get_admin()
    shop = Shop.query.filter_by(email=config['DEFAULT_SHOP_EMAIL']).first()
    command = Command(
        delivery_address=config['COMPANY_ADDRESS'],
        sended=datetime.utcnow(),
        status=Command.WAITING,
        shop=shop,
        user=admin)


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
        user = User(
            email=email, password=password, confirmed=True, is_manager=manager)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        employee = Employee(
            user=user, firstname=firstname, lastname=lastname, salary=salary)
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
        address = fk.street_address()
        shop = Shop(
            name=name, email=email, telephone=telephone, address=address)
        db.session.add(shop)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def create_foods(count=200):
    shops = Shop.query.all()
    rate_extra = 0.1
    for _ in range(count):
        name = fk.catch_phrase()
        price = (random.random() * MAX_PRICE) + MAX_PRICE
        extra = True if random.random() <= RATE_EXTRA else False
        shop = random.choice(shops)
        food = Food(name=name, price=price, extra=extra, shop=shop)
        db.session.add(food)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def create_commands(status, count=5):
    if status not in [
            Command.WAITING, Command.DONE, Command.CANCEL,
            Command.NEVER_DELIVERED
    ]:
        raise Exception(
            'provide Command.WAITING, Command.DONE, Command.CANCEL Command.NEVER_DELIVERED'
        )

    shops = Shop.query.all()
    managers = User.query.filter_by(is_manager=True).all()

    sended_minute = random.randint(MINUTE_MIN_SENDED, MINUTE_MAX_SENDED)
    recieved_minute = random.randint(MINUTE_MIN_SENDED, MINUTE_MAX_SENDED)

    for _ in range(count):
        if status == Command.WAITING:
            sended = datetime.utcnow()
            recieved = None
        elif status == Command.DONE:
            sended = datetime.utcnow() - timedelta(minutes=sended_minute)
            recieved = sended + timedelta(minutes=recieved_minute)
        else:
            sended = datetime.utcnow() - timedelta(minutes=sended_minute)
            recieved = None

        delivery_address = config['COMPANY_ADDRESS']
        shop = random.choice(shops)
        user = random.choice(managers)

        command = Command(
            delivery_address=delivery_address,
            sended=sended,
            recieved=recieved,
            status=status,
            shop=shop,
            user=user)
        db.session.add(command)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def create_orders(count=10):
    ''' the real count is multiply by the number of employers + extra order '''
    shops = Shop.query.all()
    employers = Employee.query.all()

    foods = shops.foods




    


    
