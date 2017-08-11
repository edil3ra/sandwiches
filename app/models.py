from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    is_manager = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    employee = db.relationship(
        'Employee', uselist=False, back_populates='user')
    commands = db.relationship('Command', back_populates='user')

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_employee(self):
        return False if self.employee is None else True

    @is_employee.setter
    def is_employee(self, value):
        raise AttributeError('is_employee is not settable')

    @staticmethod
    def get_admin():
        return User.query.filter_by(is_admin=True).first()


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    salary = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='employee')
    orders = db.relationship('Order', back_populates='employee')


class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128))
    telephone = db.Column(db.String(128), nullable=True)
    address = db.Column(db.String(128), nullable=True)
    foods = db.relationship('Food', back_populates='shop', lazy='dynamic')
    commands = db.relationship('Command', back_populates='shop')


class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    price = db.Column(db.String(128))
    extra = db.Column(db.Boolean, default=False)
    shop_id = db.Column(db.ForeignKey('shop.id'))
    shop = db.relationship('Shop', back_populates='foods')
    orders = db.relationship('Order', back_populates='food')


class Command(db.Model):
    '''
    WAITING: when the command is sended but not recieve yet
    CANCEL: when the command is sended and recieved
    DONE: when the command is cancel before recieved
    NEVER_DELIVERED: when the command is cancel before recieved
    '''
    WAITING = 0
    DONE = 1
    CANCEL = 2
    NEVER_DELIVERED = 3

    __tablename__ = 'command'
    id = db.Column(db.Integer, primary_key=True)
    delivery_address = db.Column(db.String(128))
    sended = db.Column(db.DateTime, default=datetime.utcnow())
    recieved = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, default=WAITING)
    shop_id = db.Column(db.ForeignKey('shop.id'))
    user_id = db.Column(db.ForeignKey('user.id'))
    shop = db.relationship('Shop', back_populates='commands')
    user = db.relationship('User', back_populates='commands')
    orders = db.relationship('Order', back_populates='command')


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.ForeignKey('food.id'))
    command_id = db.Column(db.ForeignKey('command.id'))
    employee_id = db.Column(db.ForeignKey('employee.id'), nullable=True)
    food = db.relationship('Food', back_populates='orders')
    command = db.relationship('Command', back_populates='orders')
    employee = db.relationship('Employee', back_populates='orders')
