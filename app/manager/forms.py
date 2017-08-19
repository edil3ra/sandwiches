from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField, SelectField
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


class CommandForm(FlaskForm):
    delivery_address = StringField('Where do you want your command to be delivered', validators=[Required(), Length(1, 128)])
    shop = SelectField('Choose a shop to make your command', coerce=int)
    submit = SubmitField('Command')

    def __init__(self, *args, **kwargs):
        super(CommandForm, self).__init__(*args, **kwargs)
        shops = Shop.query.order_by('name')
        self.shop.choices = [('', 'Choose a shop')]
        self.shop.choices += [(shop.id, shop.name) for shop in shops]

        
