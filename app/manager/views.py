from flask import render_template, redirect, flash, url_for, request, current_app
from flask_login import current_user

from ..models import Shop, Food, Command, Employee, Order
from .forms import ShopForm, FoodForm, CommandForm
from . import manager
from .. import db


@manager.route('/', methods=['GET', 'POST'])
def index():
    command = Command.last()

    if command.is_preparing:
        return handle_preparing(command)

    elif command.is_waiting:
        return handle_waiting(command)

    elif command.is_done:
        return handle_done(command)


def handle_preparing(command):
    extra_foods = command.shop.foods.filter_by(extra=True)
    extra_orders = command.extra_orders()
    employee_orders = command.employees_orders()

    return render_template(
        'command_preparing.html',
        command=command,
        extra_foods=extra_foods,
        extra_orders=extra_orders_format,
        employee_orders=employee_orders)


def handle_waiting(command):
    extra_orders = command.extra_orders()
    employee_orders = command.employees_orders()

    extra_orders_formatted = [{
        'food': orders[0].food.name,
        'price': Order.sum_price(orders)
    } for orders in Order.groupby(extra_orders, Order.GROUP_BY_FOOD)]

    employee_orders_formatted = [{
        'employee':
        orders[0].employee.fullname,
        'food':
        Food.format_counter_foods(
            Food.counter_foods([order.food for order in orders])),
        'price':
        Order.sum_price(orders)
    } for orders in Order.groupby(employee_orders, Order.GROUP_BY_EMPLOYEE)]

    return render_template(
        'command_waiting.html',
        command=command,
        employee_orders=employee_orders_formatted,
        extra_orders=extra_orders_formatted)


def handle_done(command):
    form = CommandForm()
    if not form.delivery_address.data:
        form.delivery_address.data = current_app.config['COMPANY_ADDRESS']

    if form.validate_on_submit():
        flash('the command was succefully added')
        command = Command(
            delivery_address=form.delivery_address.data,
            shop_id=form.shop.data,
            user=current_user)
        db.session.add(command)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('command_done.html', form=form, command=command)


@manager.route('/increment_food/<int:food_id>', methods=['GET'])
def increment_food(food_id):
    command = Command.last()
    food = Food.query.filter_by(id=food_id).first()

    if not food:
        flash('food does not exist')
        return redirect(url_for('.index'))

    order = Order(command=command, food=food)
    db.session.add(order)
    return redirect(url_for('.index'))


@manager.route('/decrement_food/<int:food_id>')
def decrement_food(food_id):
    command = Command.last()
    food = Food.query.filter_by(id=food_id).first()

    if not food:
        flash('food does not exist')
        return redirect(url_for('.index'))

    order = command.orders.filter_by(food=food).first()

    if not order:
        flash('you cant\'t have negative order ')
        return redirect(url_for('.index'))

    db.session.delete(order)
    return redirect(url_for('.index'))


@manager.route('/wait')
def wait():
    Command.last().wait()
    return redirect(url_for('.index'))


@manager.route('/send_mail_command')
def send_mail_command():
    Command.last()
    flash('Todo: send mail')
    return redirect(url_for('.index'))


@manager.route('/cancel')
def cancel():
    Command.last().cancel()
    return redirect(url_for('.index'))


@manager.route('/delivered')
def delivered():
    Command.last().delivered()
    return redirect(url_for('.index'))


@manager.route('/never_delivered')
def never_delivered():
    Command.last().never_delivered()
    return redirect(url_for('.index'))


@manager.route('/shops')
def shops():
    shops = Shop.query.all()
    return render_template('shops.html', shops=shops)


@manager.route('/shop/<int:pk>', methods=['GET', 'POST'])
def shop(pk):
    shop = Shop.query.filter_by(id=pk).first()

    if not shop:
        flash('The shop does not exist')
        return render_template('shops.html')

    foods = shop.foods.all()

    if request.method == 'POST':
        form = ShopForm()
        if form.validate_on_submit():
            if Shop.query.filter_by(name=form.name.data).first() is not None\
               and shop.name != form.name.data:
                flash('The shop: {} already exist, please try another name'.
                      format(form.name.data))
                return render_template(
                    'shop.html', shop=shop, form=form, foods=foods)

            shop.name = form.name.data
            shop.email = form.email.data
            shop.telephone = form.telephone.data
            shop.address = form.address.data
            db.session.add(shop)
            flash('The shop: {} has been updated'.format(form.name.data))
            return redirect(url_for('.shops', form=form))

    # prefill the form data
    form = ShopForm(
        name=shop.name,
        email=shop.email,
        telephone=shop.telephone,
        address=shop.address)
    return render_template('shop.html', shop=shop, form=form, foods=foods)


@manager.route('/shop/delete_<int:pk>')
def shop_delete(pk):
    shop = Shop.query.filter_by(id=pk).first()
    if not shop:
        flash('The shop does not exist')
        return render_template('shops.html')

    db.session.delete(shop)
    flash('The shop {} has been removed'.format(shop.name))
    return redirect(url_for('.shops'))


@manager.route('/shop/create', methods=['GET', 'POST'])
def shop_create():
    form = ShopForm()
    if form.validate_on_submit():
        if Shop.query.filter_by(name=form.name.data).first() is not None:
            flash('The shop: {} already exist, please try another name'.format(
                form.name.data))
            return render_template('shop_create.html', form=form)

        shop = Shop(
            name=form.name.data,
            email=form.email.data,
            telephone=form.telephone.data,
            address=form.address.data)
        db.session.add(shop)
        flash('The shop: {} has been registred'.format(form.name.data))
        return redirect(url_for('.shops'))

    return render_template('shop_create.html', form=form)


@manager.route('/food/create_<int:pk_shop>_shop', methods=['GET', 'POST'])
def food_create(pk_shop):
    shop = Shop.query.filter_by(id=pk_shop).first()
    if not shop:
        flash('You try to add food to a non existing shop')
        return redirect(url_for('.shops'))

    form = FoodForm()
    if form.validate_on_submit():
        food = Food(
            name=form.name.data,
            price=form.price.data,
            extra=form.extra.data,
            shop=shop)
        db.session.add(food)
        flash('The food: {} has been add to {}'.format(food.name, shop.name))
        return redirect(url_for('.shop', pk=pk_shop))

    return render_template('food_create.html', form=form, shop=shop)


@manager.route('/food/update_<int:pk>', methods=['GET', 'POST'])
def food_update(pk):
    food = Food.query.filter_by(id=pk).first()
    if not food:
        flash('The food does not exist')
        return redirect(url_for('.shop', pk=food.shop_id))

    if request.method == 'POST':
        form = FoodForm()
        if form.validate_on_submit():
            food.name = form.name.data
            food.price = form.price.data
            food.extra = form.extra.data
            db.session.add(food)
            flash('The food: {} has been updated'.format(form.name.data))
            return redirect(url_for('.shop', pk=food.shop_id))

    form = FoodForm(name=food.name, price=food.price, extra=food.extra)
    return render_template('food_update.html', form=form, food=food)


@manager.route('/food/delete_<int:pk>')
def food_delete(pk):
    food = Food.query.filter_by(id=pk).first()
    if not food:
        flash('The food does not exist')
        return redirect(url_for('.shop', pk=food.shop_id))

    db.session.delete(food)
    flash('The food {} has been removed'.format(food.name))
    return redirect(url_for('.shop', pk=food.shop_id))
