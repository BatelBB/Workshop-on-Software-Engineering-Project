from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.validators import NumberRange, regexp, DataRequired
from wtforms import IntegerField, SubmitField, SelectField, StringField

from src.domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("buying", __name__)


@bp.get('/store/<name>')
def view_store(name: str):
    domain = get_domain_adapter()
    response = domain.get_store(name)
    success, data, message = response.success, response.result, response.description
    permissions = {p.name for p in domain.permissions_of(name)}
    basket = domain.get_basket(name)
    if not basket.success:
        flash(basket.description, category="danger")
        return redirect(url_for('home.home'))
    return render_template(
        "buying/view_store.html", name=name,
        success=success, message=message,
        products=data,
        permissions=permissions, basket=basket.result
    )


class BuyProductForm(FlaskForm):
    amount = IntegerField(label="amount (0 for removing from cart)", validators=[NumberRange(min=0)])
    submit = SubmitField(label='update my cart')


@bp.route('/store/<store_name>/buy/<product_name>', methods=('GET', 'POST'))
def buy_product(store_name: str, product_name: str):
    domain = get_domain_adapter()
    basket = domain.get_basket(store_name)
    if not basket.success:
        flash(basket.description, category="danger")
        return redirect(url_for('home.home'))
    product = domain.get_product(store_name, product_name)
    if not product.success:
        flash(product.description, category="danger")
        return redirect(url_for('home.home'))
    amount = basket.result.amounts[product_name] if product_name in basket.result.amounts else None
    form = BuyProductForm()
    if form.validate_on_submit(extra_validators={"amount": [NumberRange(max=product.result.quantity)]}):
        update_basket = domain.update_cart_product_quantity(store_name, product_name,
                                                            form.amount.data - (amount or 0))
        if update_basket.success:
            flash(
                f"You have succesfully updated your basket in store {store_name}: {form.amount.data} of {product_name}",
                category="success")
            return redirect(url_for('buying.view_store', name=store_name))
        else:
            flash(update_basket.description, category="danger")
    return render_template("buying/buy_product.html",
                           product=product.result, store_name=store_name, amount=amount, form=form
                           )


@bp.get('/cart')
def view_cart():
    domain = get_domain_adapter()
    cart = domain.get_cart()
    cart_price = domain.get_cart_price()
    return render_template("buying/view_cart.html", cart=cart, cart_price=cart_price)


class CheckoutTypeSelectionForm(FlaskForm):
    type = SelectField(label='payment type', choices=['card'])
    submit = SubmitField(label='Submit')


@bp.route('/checkout_cart', methods=('GET', 'POST'))
def checkout_cart():
    form = CheckoutTypeSelectionForm()
    if form.validate_on_submit():
        type = form.type.data
        if type == "card":
            return redirect(url_for('buying.buy_with_card'))
    return render_template('buying/checkout_cart.html', form=form)


class BuyWithCardForm(FlaskForm):
    number = StringField(label='credit card number', validators=[regexp(r'[\d]+', message='digits only plz')])
    exp_month = IntegerField(label='expiration month', validators=[NumberRange(min=1, max=12)])
    exp_year = IntegerField(label='expiration year', validators=[NumberRange(min=2023, max=2100)])
    ccv = StringField(label='CCV', validators=[regexp(r'\d\d\d', message='3 digits please')])
    street = StringField(label='street', validators=[DataRequired()])
    apt_number = IntegerField(label='apartment number', validators=[NumberRange(min=1)])
    city = StringField(label='city', validators=[DataRequired()])
    country = StringField(label='country', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


@bp.route('/buy_with_card', methods=('GET', 'POST'))
def buy_with_card():
    form = BuyWithCardForm()
    fields = [form.number, form.exp_month, form.exp_year,
              form.ccv, form.street, form.apt_number, form.city, form.country]
    if form.validate_on_submit():
        domain = get_domain_adapter()
        response = domain.purchase_by_card(*(field.data for field in fields))
        if response.success:
            flash('Purchase successful', category='success')
            return redirect(url_for('home.home'))
        else:
            flash(response.description, category='danger')
    return render_template('buying/buy_with_card.html', form=form, fields=fields)
