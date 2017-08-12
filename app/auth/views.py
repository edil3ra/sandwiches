from flask import render_template
from . import auth


@auth.route('/')
def index():
    return render_template('auth/login.html')


