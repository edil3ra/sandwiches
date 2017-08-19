from flask import render_template, flash, redirect, request, url_for

from flask_login import login_user, login_required, logout_user

from . import auth

from .. import db
from ..models import User, Employee
from .forms import LoginForm, RegistrationEmployeeForm, RegistrationForm


@auth.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, True)
            flash('You are now logged')
            if user.is_manager:
                return redirect(url_for('manager.index'))
            elif user.is_employee:
                return redirect(url_for('main.index'))
            else:
                return redirect(request.args.get('next') or url_for('main.index'))
                
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth.route('/register-manager', methods=['GET', 'POST'])
def register_manager():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            is_manager=True
        )
        db.session.add(user)
        db.session.commit()
        login_user(user, True)
        flash('You are registred as a manager with mail:{}'.format(user.email))
        return redirect(url_for('main.index'))
    return render_template('register_manager.html', form=form)



@auth.route('/register-employee', methods=['GET', 'POST'])
def register_employee():
    form = RegistrationEmployeeForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            is_manager=form.is_manager.data
        )

        employee = Employee(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            salary=form.salary.data
        )
        
        user.employee = employee
        db.session.add(user)
        db.session.commit()
        
        login_user(user, True)
        if form.is_manager.data:
            flash('You are registerd as an employee and manager with mail:{}'.format(user.email))
            return redirect(url_for('manager.index'))
        else:
            flash('You are registerd as an employe with mail:{}'.format(user.email))
            return redirect(url_for('main.index'))
            

    return render_template('register_employee.html', form=form)



