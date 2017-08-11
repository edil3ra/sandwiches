import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Employee, Shop, Food
from utils import fixtures as fx




app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(
        app=app,
        fx=fx,
        fk= fx.fk,
        db=db,
        User=User,
        Employee=Employee,
        Shop=Shop,
        Food=Food,
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



def fixtures_creation():
    fixtures = [
        {
            'message': 'Managers creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {'count': 3 },
        },
        {
            'message': 'Employees creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {'count': 25 },
        },
        {
            'message': 'Employees as manager creation',
            'function': fx.create_employees,
            'args': [],
            'kwargs': {'count': 5, 'manager': True },
        },
        {
            'message': 'Shops creation',
            'function': fx.create_shops,
            'args': [],
            'kwargs': {'count': 5 },
        },
        {
            'message': 'foods creation',
            'function': fx.create_foods,
            'args': [],
            'kwargs': {'count': 120 },
        },
        
    ]    
    
    for i, d in enumerate(fixtures):
        message, function, args, kwargs = d['message'], d['function'], d['args'], d['kwargs'], 
        print('{}/{} -- start {} with {}  and {} '\
              .format(i+1, len(fixtures), message, args, kwargs))
        d['function'](*args, **kwargs)
        print('{}/{} -- end {} with {} args  {} '.\
              format(i+1, len(fixtures), message, args, kwargs))

    
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


    print('Start fixture creation')
    fixtures_creation()
    print('End fixture creation')


    

        
        

    
if __name__ == '__main__':
    manager.run()
