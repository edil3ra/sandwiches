from flask import render_template, redirect, flash, url_for
from ..models import Shop
from .forms import ShopForm
from . import manager
from .. import db


@manager.route('/')
def index():
    return render_template('index.html')


@manager.route('/shops')
def shops():
    shops = Shop.query.all()
    return render_template('shops.html', shops=shops)


@manager.route('/shop/<int:pk>', methods=['GET', 'POST'])
def shop(pk):
    shop = Shop.query.filter_by(id=pk).first()
    foods = shop.foods.all()
    form = ShopForm()
    if not shop:
        flash('The shop id does not exist')
        return render_template('shops.html')
    return render_template('shop.html', shop=shop, form=form, foods=foods)

    


@manager.route('/shop/delete_<int:pk>')
def shop_delete(pk):
    shop = Shop.query.filter_by(id=pk).first()
    if not shop:
        flash('The shop id does not exist')
        return render_template('shops.html')

    db.session.delete(shop)
    flash('The shop {} is remove'.format(shop.name))
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
        return redirect(url_for('.shops', form=form))

    return render_template('shop_create.html', form=form)



