from collections import OrderedDict

from flask import render_template, redirect, flash, url_for, request, current_app, g, abort, session
from flask_login import current_user, login_required

from ..decorators import manager_required
from ..models import Shop, Food, Command, Employee, Order
from .forms import ShopForm, FoodForm, CommandForm
from . import manager
from .. import db
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


@manager.before_request
@login_required
@manager_required
def protect_manager_blueprint():
    if not current_user.is_manager:
        flash('You are not a manager')
        return redirect(url_for('auth.login'))
    else:
        pass


@manager.before_request
def active_sidenav():
    url = request.path.rstrip('/').split('/')[2]
    g.sidenav = url if url else 'default'


@manager.route('/home', methods=['GET', 'POST'])
def index():
    command = Command.last()

    if command is None:
        flash(
            'This is you first command, you  have to at least register one shop before making command'
        )
        return handle_done()

    if command.is_preparing:
        return handle_preparing(command)

    elif command.is_waiting:
        return handle_waiting(command)

    elif command.is_done:
        return handle_done()


def handle_preparing(command):
    extra_foods = command.shop.foods.filter_by(extra=True).order_by(Food.name)
    food_count_dict = Food.counter_foods(
        [order.food for order in command.extra_orders()])
    employee_orders = command.employees_orders().join(Employee).order_by(
        Employee.firstname)

    extra_foods_formatted = [
        OrderedDict(
            zip(["id", "name", "price", "count"], [
                food.id, food.name, food.price,
                food_count_dict.get(food.name) or 0
            ])) for food in extra_foods
    ]

    employee_orders_formatted = [
        OrderedDict(
            zip(["employee", "food", "price"], [
                orders[0].employee.fullname,
                Food.format_counter_foods(
                    Food.counter_foods([order.food for order in orders])),
                Order.sum_price(orders),
            ]))
        for orders in Order.groupby(employee_orders, Order.GROUP_BY_EMPLOYEE)
    ]

    return render_template(
        'command_preparing.html',
        command=command,
        extra_foods=extra_foods_formatted,
        employee_orders=employee_orders_formatted)


def handle_waiting(command):
    extra_orders = command.extra_orders().join(Food).order_by(Food.name)
    employee_orders = command.employees_orders().join(Employee).order_by(
        Employee.firstname)

    extra_orders_formatted = [{
        'food': orders[0].food.name,
        'price': Order.sum_price(orders)
    } for orders in Order.groupby(extra_orders, Order.GROUP_BY_FOOD)]

    # OrderDict is not orderd if sended by as kwargs arguments in python2
    extra_orders_formatted = [
        OrderedDict(
            zip(["food", "price"],
                [orders[0].food.name,
                 Order.sum_price(orders)]))
        for orders in Order.groupby(extra_orders, Order.GROUP_BY_FOOD)
    ]

    # OrderDict is not orderd if sendeb by as kwargs arguments in python2
    employee_orders_formatted = [
        OrderedDict(
            zip(["employee", "food", "price"], [
                orders[0].employee.fullname,
                Food.format_counter_foods(
                    Food.counter_foods([order.food for order in orders])),
                Order.sum_price(orders),
            ]))
        for orders in Order.groupby(employee_orders, Order.GROUP_BY_EMPLOYEE)
    ]

    return render_template(
        'command_waiting.html',
        command=command,
        employee_orders=employee_orders_formatted,
        extra_orders=extra_orders_formatted)


def handle_done():
    form = CommandForm()
    if not form.delivery_address.data:
        form.delivery_address.data = current_app.config['COMPANY_ADDRESS']

    if form.validate_on_submit():
        flash('the command was succefully added')
        new_command = Command(
            delivery_address=form.delivery_address.data,
            shop_id=form.shop.data,
            user=current_user)
        db.session.add(new_command)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('command_done.html', form=form)


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
    flash('you have validate the current command')
    return redirect(url_for('.index'))


@manager.route('/send_mail_command')
def send_mail_command():
    Command.last()
    flash('Todo: send mail')
    return redirect(url_for('.index'))


@manager.route('/cancel')
def cancel():
    '''should send an email to all employee that registred a command'''
    Command.last().cancel()
    flash('you have cancel the current command, please inform your employees')
    return redirect(url_for('.index'))


@manager.route('/delivered')
def delivered():
    Command.last().delivered()
    flash('The command was succefully delivered')
    return redirect(url_for('.index'))


@manager.route('/never_delivered')
def never_delivered():
    Command.last().never_delivered()
    flash('The command was never delivered')
    return redirect(url_for('.index'))


@manager.route('/shops')
def shops():
    shops = Shop.query.order_by(Shop.name)
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


@manager.route('/food/create_<int:pk>_shop', methods=['GET', 'POST'])
def food_create(pk):
    shop = Shop.query.filter_by(id=pk).first()
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
        return redirect(url_for('.shop', pk=pk))

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


@manager.route('/employees/')
@manager.route('/employees/<int:offset_month>')
def employees(offset_month=0):

    start_date = datetime.today().replace(day=1) - relativedelta(
        months=offset_month)
    end_date = start_date + relativedelta(months=1) - relativedelta(days=1)

    first_ordered_date = Command.query.filter(
        Command.status.in_([Command.DELIVERED, Command.NEVER_DELIVERED
                            ])).order_by(Command.recieved).first().recieved
    
    last_ordered_date = Command.query.filter(
        Command.status.in_([Command.DELIVERED, Command.NEVER_DELIVERED])
    ).order_by(Command.recieved.desc()).first().recieved

    pagination = {
        'is_previous_month': end_date - relativedelta(months=1) >= first_ordered_date,
        'is_next_month': start_date + relativedelta(months=1) <= last_ordered_date,
        'is_previous_year': end_date - relativedelta(years=1) >= first_ordered_date,
        'is_next_year': start_date + relativedelta(years=1) <= last_ordered_date
    }

    orders = db.session.query(Order, db.func.sum(Food.price))\
    .join(Order.command)\
    .join(Order.employee)\
    .join(Order.food)\
    .filter(Order.employee != None)\
    .filter(Command.status.in_([Command.DELIVERED, Command.NEVER_DELIVERED]))\
    .filter(start_date <= Command.recieved)\
    .filter(end_date >= Command.recieved)\
    .group_by(Order.employee_id)

    employees_formatted = [
        OrderedDict(
            zip(["name", "salary", "monthly expenses", "Net salary"], [
                order.employee.fullname, order.employee.salary, expense,
                order.employee.salary - expense
            ])) for order, expense in orders.all()
    ]

    return render_template(
        'employees.html',
        employees=employees_formatted,
        current_date=start_date,
        current_offset=offset_month,
        pagination=pagination
    )


@manager.route('/commands')
def commands():
    page = int(request.args.get('page') or current_app.config['DEFAULT_PAGE'])
    per_page = int(request.args.get('per_page') or current_app.config['DEFAULT_PER_PAGE'])
    commands = Command.query.filter(Command.status.in_([Command.DELIVERED, Command.NEVER_DELIVERED]))\
                            .order_by(Command.id.desc())
    pagination = commands.paginate(page, per_page)
    commands_indexed = enumerate(pagination.items)

    session['page'] = page
    session['per_page'] = per_page
    
    print(session)
    
    return render_template('commands.html', commands=commands_indexed, Command=Command, pagination=pagination)



@manager.route('/command/<int:pk>')
def command(pk):
    command = Command.query.filter_by(id=pk).first()
    if not command:
        abort(404)
    return render_template('command.html', command=command)

