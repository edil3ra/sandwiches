import os
import urllib

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask import url_for

from app import create_app, db, auth
from app.models import User, Employee, Shop, Food, Command, Order
from utils import fixtures as fx
from datetime import datetime, timedelta, date

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

from flask_login import current_user


def make_shell_context():
    return dict(
        app=app,
        current_user=current_user,
        auth=auth,
        fx=fx,
        fk=fx.fk,
        db=db,
        User=User,
        Employee=Employee,
        Shop=Shop,
        Food=Food,
        Order=Order,
        Command=Command,
        l=Command.last(),
        datetime=datetime,
        date=date,
        timedelta=timedelta,
    )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


def fixtures_creation():
    fixtures = [
        {
            'message': 'Managers creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {
                'count': 2
            },
        },
        {
            'message': 'Employees creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {
                'count': 10
            },
        },
        {
            'message': 'Employees as manager creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {
                'count': 3,
                'manager': True
            },
        },
        {
            'message': 'Shops creation',
            'function': fx.create_shops,
            'args': [],
            'kwargs': {
                'count': 5
            },
        },
        {
            'message': 'Foods creation',
            'function': fx.create_foods,
            'args': [],
            'kwargs': {
                'count_by_shop': 20
            },
        },
        {
            'message': 'Not Delivered commands creation',
            'function': fx.create_commands,
            'args': [],
            'kwargs': {
                'count': 8,
                'status': Command.NEVER_DELIVERED
            },
        },
        {
            'message': 'Delivered commands creation',
            'function': fx.create_commands,
            'args': [],
            'kwargs': {
                'count': 45,
                'status': Command.DELIVERED
            },
        },
        {
            'message': 'orders creation',
            'function': fx.create_orders,
            'args': [],
            'kwargs': {},
        },
    ]

    for i, d in enumerate(fixtures):
        message, function, args, kwargs = d['message'], d['function'], d[
            'args'], d['kwargs'],
        print('{}/{} -- start {} with {}  and {} '\
              .format(i+1, len(fixtures), message, args, kwargs))
        d['function'](*args, **kwargs)
        print('{}/{} -- end {} with {} args  {} '.\
              format(i+1, len(fixtures), message, args, kwargs))

@manager.command
def reset_db():
    '''
    Reset the db
    '''
    db.drop_all()
    db.create_all()

    print('Start default admin creation')
    fx.create_default_admin()
    print('End default admin creation')
    
        
@manager.command
def fill_db():
    '''
    Create the database with an administrator and random datas
    '''

    db.drop_all()
    db.create_all()

    print('Start default admin creation')
    fx.create_default_admin()
    print('End default admin creation')

    print('Start default shop creation')
    fx.create_default_shop()
    print('End default shop creation')


    print('\n\n--------------\n\n')

    print('Start fixture creation')
    fixtures_creation()
    print('End fixture creation')



@manager.command
def command_prepare():
    '''Register a new command'''
    delivery_address = app.config['COMPANY_ADDRESS']
    shop_id = input('shop id: ')
    user_id = input('user id:')
    db.session.add(Command(delivery_address=delivery_address, shop_id=shop_id, user_id=user_id))


@manager.command
def command_prepare_auto():
    '''Register a command with user_id = 1 and shop_id = 1'''
    delivery_address = app.config['COMPANY_ADDRESS']
    db.session.add(Command(delivery_address=delivery_address, shop_id=1, user_id=1))
    
    
@manager.command
def command_wait():
    '''Set the current command status to wait'''
    Command.last().wait()

    
@manager.command
def command_delivered():
    '''Set the current command status to delivered'''
    Command.last().delivered()

    
@manager.command
def command_never_delivered():
    '''Set the current command status to not delivered'''
    Command.last().delivered()

@manager.command
def random_orders():
    '''Make random orders for the current command'''
    fx.randomize_last_command_orders()
    
    
@manager.command
def routes():
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)
    

if __name__ == '__main__':
    manager.run()


