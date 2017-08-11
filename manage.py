import os

from app import create_app, db
from app.models import User, Employee
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from utils import fixtures as fx




app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, fx=fx, db=db, User=User, Employee=Employee)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



def admin_creation():
    admin_email = os.environ.get('ADMIN_EMAIL') or 'vincent.houba.test@gmail.com'
    admin_password = os.environ.get('ADMIN_PASSWORD') or 'password'
    admin = User(email=admin_email, password=admin_password, confirmed=True, is_admin=True, is_manager=True)
    db.session.add(admin)
    db.session.commit()
    admin_employee = Employee(firstname='Vincent', lastname='Houba', salary=2000, user=admin)
    db.session.add(admin_employee)
    db.session.commit()

    
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
    ]    
    
    for i, d in enumerate(fixtures):
        message, function, args, kwargs = d['message'], d['function'], d['args'], d['kwargs'], 
        print('{}/{} -- start {} with {}  and {} '\
              .format(i+1, len(fixtures)+1, message, args, kwargs))
        d['function'](*args, **kwargs)
        print('{}/{} -- end {} with {} args  {} '.\
              format(i+1, len(fixtures)+1, message, args, kwargs))

    
@manager.command
def fill_db():
    '''
    Create the database with an administrator and random datas
    '''
    
    db.drop_all()
    db.create_all()

    print('Start admin creation')
    admin_creation()
    print('End admin creation')


    print('Start fixture creation')
    fixtures_creation()
    print('End fixture creation')


    

        
        

    
if __name__ == '__main__':
    manager.run()
