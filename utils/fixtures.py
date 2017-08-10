import os
from app.models import User
from app import db



def create_admin():
    email=os.environ.get('ADMIN_EMAIL') or 'admin'
    password=os.environ.get('ADMIN_PASSWORD') or 'admin'
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
