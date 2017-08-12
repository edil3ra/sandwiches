from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from ..models import User, Employee

class LoginForm(FlaskForm):
    email = StringField('Type your Email', validators=[Required(), Length(1, 128),
                                             Email()])
    password = PasswordField('Type your Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')




class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 128),
                                           Email()])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')



class RegistrationEmployeeForm(RegistrationForm):
    firstname = StringField('Firstname', validators=[Required(), Length(1, 128)])
    lastname = StringField('Lastname', validators=[Required(), Length(1, 128)])
    salary = IntegerField('Salary')
    is_manager = BooleanField('Check if you want to be a manager')


    
