from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("selling", __name__)


class CreateStoreForm(FlaskForm):
    name = StringField(validators=[validation.DataRequired()])
    submit = SubmitField()


@bp.route('/create_store', methods=('GET', 'POST'))
def create_store():
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to create a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    form = CreateStoreForm()
    error = None
    if form.validate_on_submit():
        store_name = form.name.data
        res = domain.open_store(store_name)
        if res.success:
            flash(f"You've created a store {store_name}. Here's hoping bussiness goes well!", category="success")
            return redirect(url_for("home.home"))
        error = res.description
        flash(error, category="danger")
    return render_template("selling/create_store.html", form=form, error=error)


class AddProductForm(FlaskForm):
    product_name = StringField(validators=[validation.Length(min=3, max=100)])
    category = StringField(validators=[validation.DataRequired()])
    price = FloatField(validators=[validation.NumberRange(min=0.01)])
    quantity = IntegerField(validators=[validation.NumberRange(min=0)])
    submit = SubmitField()


@bp.route('/add_product/<store_name>', methods=('POST', 'GET'))
def add_product(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to create a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.Add.name not in perms:
        flash("Not allowed to add products to this store")
        return redirect(url_for("buying.view_store", name=store_name))

    form = AddProductForm()
    error = None
    if form.validate_on_submit():
        product_name = form.product_name.data
        category = form.category.data
        price = form.price.data
        qty = form.quantity.data
        res = domain.add_product(store_name, product_name, category, price, qty)
        if res.success:
            flash(f"You've added a product!", category="success")
            return redirect(url_for("buying.view_store", name=store_name))
        error = res.description
        flash(error, category="danger")
    return render_template("selling/add_product.html", form=form, error=error)
