from flask import render_template, redirect, url_for, flash
from . import main
from ..decorators import employee_required
from flask_login import current_user, login_required

@main.before_request
@login_required
@employee_required
def before_request():
    flash('hello')
    if not current_user.is_employee:
        flash('user')
        return redirect(url_for('auth.login'))
    else:
        pass

@main.route('/')
def index():
    return render_template('main/index.html')


