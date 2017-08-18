import os
import math
import random
from datetime import datetime, timedelta
from faker import Factory

from sqlalchemy.exc import IntegrityError

from app.models import User, Employee, Shop, Food, Command, Order
from app import create_app, db
import fixtures_data


MIN_SALARY = 1300
MAX_SALARY = 3000

MIN_PRICE = 3
MAX_PRICE = 50

RATE_EXTRA_CREATION = 0.1
RATE_EXTRA_ORDER = 0.1

RATE_EXTRA_COMMANDED_MIN = 1
RATE_EXTRA_COMMANDED_MAX = 4

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
        status=Command.PREPARING,
        shop=shop,
        user=admin)


def create_managers(count=5):
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


def create_employees(count=10, manager=False):
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


def create_foods(count_by_shop=20, rate_extra=RATE_EXTRA_CREATION):
    count_by_shop_extra = int(math.floor(count_by_shop * rate_extra) + 1)
    shops = Shop.query.all()
    foods = []
    for shop in shops:
        foods_choice = random.sample(fixtures_data.foods, count_by_shop)
        foods_extra_choice = random.sample(fixtures_data.foods_extra, count_by_shop_extra)
        price_choice = [round((random.random() * MAX_PRICE) + MAX_PRICE, 2)
                        for _ in range(count_by_shop)]
        price_extra_choice = [round((random.random() * MAX_PRICE) + MAX_PRICE, 2)
                              for _ in range(count_by_shop_extra)]
        
        for i in range(count_by_shop):
            food = Food(name=foods_choice[i], price=price_choice[i], extra=False,shop=shop)
            foods.append(food)
        for i in range(count_by_shop_extra):
            food = Food(name=foods_extra_choice[i], price=price_extra_choice[i], extra=True, shop=shop)
            foods.append(food)


    db.session.add_all(foods)
    db.session.commit()
            

        

def create_commands(status=Command.DELIVERED, count=5):
    if status not in [Command.DELIVERED, Command.NEVER_DELIVERED]:
        raise Exception('Command.DELIVERED Command.NEVER_DELIVERED')

    shops = Shop.query.all()
    managers = User.query.filter_by(is_manager=True).all()

    sended_minute = random.randint(MINUTE_MIN_SENDED, MINUTE_MAX_SENDED)
    recieved_minute = random.randint(MINUTE_MIN_SENDED, MINUTE_MAX_SENDED)

    for _ in range(count):
        if status == Command.DELIVERED:
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


def create_orders():
    ''' create order for each commands '''
    commands = Command.query.all()
    employees = Employee.query.all()
    orders = []
    for command in commands:
        foods = command.shop.foods.filter_by(extra=False).all()
        foods_extra = command.shop.foods.filter_by(extra=True).all()
        extra_count = random.randint(
            0, (math.floor(Employee.query.count() * RATE_EXTRA_ORDER) + 1))

        for employee in employees:
            order = Order(
                food=random.choice(foods), command=command, employee=employee)
            orders.append(order)

        for _ in range(extra_count):
            for _ in range(random.randint(RATE_EXTRA_COMMANDED_MIN, RATE_EXTRA_COMMANDED_MAX)):
                order = Order(food=random.choice(foods_extra), command=command)
                orders.append(order)

        db.session.add_all(orders)
        db.session.commit()


def randomize_last_command_orders():
    ''' update order for each commands '''
    command = Command.last().empty_orders()
    employees = Employee.query.all()
    orders = []
    
    
    foods = command.shop.foods.filter_by(extra=False).all()
    foods_extra = command.shop.foods.filter_by(extra=True).all()
    extra_count = random.randint(
        0, (math.floor(Employee.query.count() * RATE_EXTRA_ORDER) + 1))

    for employee in employees:
        order = Order(
            food=random.choice(foods), command=command, employee=employee)
        orders.append(order)

            
    for food_extra in foods_extra:
        extra_count = random.randint(RATE_EXTRA_COMMANDED_MIN, RATE_EXTRA_COMMANDED_MAX)
        orders += [Order(food=food_extra, command=command) for _ in range(extra_count)]

            
            
    db.session.add_all(orders)
    db.session.commit()


    
