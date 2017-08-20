from flask import render_template, redirect, url_for, flash, request, g
from . import employee
from ..decorators import employee_required
from flask_login import current_user, login_required

@employee.before_request
@login_required
@employee_required
def protect_employee_blueprint():
    if not current_user.is_employee:
        flash('user')
        return redirect(url_for('auth.login'))
    else:
        pass

    
@employee.before_request
def active_sidenav():
    try:
        g.sidenav = request.path.rstrip('/').split('/')[1]
    except IndexError:
        g.sidenav = 'default'


@employee.route('/')
@employee.route('/home')
def index():
    return render_template('employee/index.html')


