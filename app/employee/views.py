from . import employee
from .. import db
from ..decorators import employee_required
from flask import flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..models import Command, Employee, Order, Food


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


@employee.before_request
def active_sidenav():
    command = Command.last()
    if not command:
        return render_template('employee/index_first.html')
    g.current_command = command
    

        

@employee.route('/', methods=['GET', 'POST'])
@employee.route('/home', methods=['GET', 'POST'])
def index():
    command = g.current_command
    orders_with_foods_count_and_price =\
    db.session.query(Order, db.func.count(Food.name), db.func.sum(Food.price))\
                       .join(Employee)\
                       .join(Command)\
                       .join(Food)\
                       .filter(Order.employee == current_user.employee)\
                       .filter(Order.command == command)\
                       .group_by(Food.name)

    orders, orders_count, orders_price = zip(*orders_with_foods_count_and_price)
    foods = [order.food for order in orders]

    foods_details = { food.name: {'count': count, 'total': price, 'count_style': min(count, 4)}
                      for food, count, price in
                      zip(foods, orders_count, orders_price) }
    
    total_employee = sum(orders_price)

    return render_template('employee/index.html',
                           command=command,
                           orders=orders,
                           orders_count=orders_count,
                           orders_price=orders_price,
                           foods_details=foods_details,
                           total_employee=total_employee)




@employee.route('/add_order/<int:food_id>', methods=['GET'])
def add_order(food_id):
    command = g.current_command
    employee = current_user.employee
    food = Food.query.filter_by(id=food_id).first()
    
    if not food:
        abort(403)
    
    order = Order(command=command, employee=employee, food=food)
    db.session.add(order)
    return redirect(url_for('.index'))


@employee.route('/remove_order/<int:food_id>', methods=['GET'])
def remove_order(food_id):
    command = g.current_command
    food = Food.query.filter_by(id=food_id).first()
    employee = current_user.employee

    if not food:
        abort(403)

    order = Order.query.filter_by(food=food)\
                       .filter_by(command=command)\
                       .filter_by(employee=employee).first()
    
    if not order:
        abort(403)
        
        
    db.session.delete(order)
    return redirect(url_for('.index'))
