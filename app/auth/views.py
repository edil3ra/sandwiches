from flask import render_template, flash
from . import auth
from .forms import LoginForm
from ..models import User

@auth.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flash('Login succeded')
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)



