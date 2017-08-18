from datetime import datetime
from itertools import groupby

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from . import db, login_manager



class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    is_manager = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    employee = db.relationship(
        'Employee', uselist=False, back_populates='user')
    commands = db.relationship(
        'Command', back_populates='user', lazy='dynamic')

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


class AnonymousUser(AnonymousUserMixin):
    def is_manager(self):
        return False

    def is_admin(self):
        return False

    def is_employee(self):
        return False
    
login_manager.anonymous_user = AnonymousUser

#find the user by id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    salary = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='employee')
    orders = db.relationship(
        'Order', back_populates='employee', lazy='dynamic')


class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128))
    telephone = db.Column(db.String(128))
    address = db.Column(db.String(128))
    foods = db.relationship('Food', back_populates='shop', lazy='dynamic')
    commands = db.relationship(
        'Command', back_populates='shop', lazy='dynamic')


class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    price = db.Column(db.Float)
    extra = db.Column(db.Boolean, default=False)
    shop_id = db.Column(db.ForeignKey('shop.id'))
    shop = db.relationship('Shop', back_populates='foods')
    orders = db.relationship('Order', back_populates='food', lazy='dynamic')

    
        

class Command(db.Model):
    '''
    PREPARING: when the command is not sended
    WAITING: when the command is sended but not recieve yet
    DELIVERED: when the command is recieved
    NEVER_DELIVERED: when the command is canceled because it was neve delivered
    '''
    PREPARING = 0
    WAITING = 1
    DELIVERED = 2
    NEVER_DELIVERED = 3

    __tablename__ = 'command'
    id = db.Column(db.Integer, primary_key=True)
    delivery_address = db.Column(db.String(128))
    sended = db.Column(db.DateTime, nullable=True)
    recieved = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, default=PREPARING)
    shop_id = db.Column(db.ForeignKey('shop.id'))
    user_id = db.Column(db.ForeignKey('user.id'))
    shop = db.relationship('Shop', back_populates='commands')
    user = db.relationship('User', back_populates='commands')
    orders = db.relationship('Order', back_populates='command', lazy='dynamic')


    @property
    def is_preparing(self):
        return self.status == Command.PREPARING

    @property
    def is_waiting(self):
        return self.status == Command.WAITING

    @property
    def is_delivered(self):
        return self.status == Command.DELIVERED

    @property
    def is_never_delivered(self):
        return self.status == Command.NEVER_DELIVERED

    @property
    def is_done(self):
        return self.is_delivered or self.is_never_delivered


    def cancel(self):
        db.session.delete()
        return self

    
    def wait(self):
        self.status = Command.WAITING
        self.sended = datetime.utcnow()
        db.session.add(self)
        return self

        
    def delivered(self):
        self.status = Command.DELIVERED
        self.recieved = datetime.utcnow()
        db.session.add(self)
        return self

        
    def never_delivered(self):
        self.status = Command.NEVER_DELIVERED
        db.session.add(self)
        return self


    def add_order(self, order):
        self.orders.append(order)
        db.session.add(self)
        return self

        
    def employees_orders(self):
        return self.orders.filter(Order.employee != None)


    def extra_orders(self):
        return self.orders.filter(Order.employee == None)


        
    def empty_orders(self):
        '''trash the orders of the command'''
        self.orders = []
        db.session.add(self)
        return self
        

    def switch_shop(self, shop):
        '''empty the orders of the current command and change the shop '''
        self.empty_orders()
        self.shop = shop
        db.session.add(self)
        return self
        
    
    def sum_price_employee(self):
        return sum([order.food.price for order in self.orders.filter(Order.employee != None)])

    def sum_price_extra(self):
        return sum([order.food.price for order in self.orders.filter(Order.employee == None)])

    def sum_price_total(self):
        return sum([order.food.price for order in self.orders])

        
    
    @staticmethod
    def last():
        '''return the last command'''
        return Command.query.order_by(Command.id.desc()).first()


    
class Order(db.Model):
    GROUP_BY_FOOD = 'food'
    GROUP_BY_COMMAND = 'command'
    GROUP_BY_EMPLOYEE = 'employee'
    GROUP_BY_FOOD_ID = 'food_id'
    GROUP_BY_COMMAND_ID = 'command_id'
    GROUP_BY_EMPLOYEE_ID = 'employee_id'
    
    
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.ForeignKey('food.id'))
    command_id = db.Column(db.ForeignKey('command.id'))
    employee_id = db.Column(db.ForeignKey('employee.id'), nullable=True)
    food = db.relationship('Food', back_populates='orders')
    command = db.relationship('Command', back_populates='orders')
    employee = db.relationship('Employee', back_populates='orders')


    @staticmethod
    def groupby(orders, key=GROUP_BY_FOOD):
        '''return List of orders formated by group
        Paramaters
        ----------
        orders: List Order
        key: str -- must be an attribute of the object
        Returns
        ------
        List List<Order> -- return a list of list groupby object attribute
        '''
        return [list(group) for _, group in groupby(orders, lambda order: getattr(order, key))]
        

        
        

        
