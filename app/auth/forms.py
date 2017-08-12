from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError



class LoginForm(FlaskForm):
    email = StringField('Type your Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Type your Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
