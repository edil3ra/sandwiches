from flask import render_template
from . import manager


@manager.route('/')
def index():
    return render_template('manager/index.html')


