from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError

from ..models import Shop

class ShopForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(1, 128)])
    email = StringField('Email', validators=[Required(), Length(1, 128), Email()])
    telephone = StringField('Telephone', validators=[Required(), Length(1, 128)])
    address = StringField('Address', validators=[Required(), Length(1, 128)])
    submit = SubmitField('Validate')



class FoodForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(1, 128)])
    price = FloatField('Price', validators=[Required()])
    extra = BooleanField('Is this an extra food?')
    submit = SubmitField('Validate')





