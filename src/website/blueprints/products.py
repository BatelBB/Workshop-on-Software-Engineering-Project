from typing import List

from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from src.domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter
from website.core_features.domain_access.session_adapter_dto import ProductDto

bp = Blueprint("products", __name__)


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
    return render_template("products/add_product.html", form=form, error=error)


class EditProductForm_one_field(FlaskForm):
    field_to_change = SelectField('Choose field to edit', choices=[('name', 'Name'), ('category', 'Category'),
                                                                   ('price', 'Price'), ('quantity', 'Quantity')],
                                  validators=[validation.DataRequired()])
    new_value = StringField('New value', validators=[validation.DataRequired()])
    submit = SubmitField()


# remove product
@bp.route("/remove_product/<store_name>/<product_name>", methods=['POST','GET','DELETE'])
def remove_product(store_name: str, product_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to create a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.Remove.name not in perms:
        flash("Not allowed to delete products from this store")
        return redirect(url_for("buying.view_store", name=store_name))
    store_response = domain.get_store(store_name)
    if not store_response.success:
        flash(store_response.description)
        return redirect(url_for('home.home'))
    matching: List[ProductDto] = [p for p in store_response.result if p.name == product_name]
    if len(matching) == 0:
        flash(f"no such product found: {store_name}/{product_name}")
        return redirect(url_for("buying.view_store", name=store_name))
    res = domain.remove_product(store_name, product_name)
    if res.success:
        flash(f"You've removed product {product_name}!", category="success")
        return redirect(url_for("buying.view_store", name=store_name))
    else:
        error = res.description
        flash(error, category="danger")
        return redirect(url_for("buying.view_store", name=store_name))

# update product's one field
@bp.route('/edit_product_one_field/<store_name>/<product_name>', methods=('POST', 'GET'))
def edit_product_one_field(store_name: str, product_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to create a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.Update.name not in perms:
        flash("Not allowed to update products to this store")
        return redirect(url_for("buying.view_store", name=store_name))
    store_response = domain.get_store(store_name)
    if not store_response.success:
        flash(store_response.description)
        return redirect(url_for('home.home'))
    mathching: List[ProductDto] = [p for p in store_response.result if p.name == product_name]
    if len(mathching) == 0:
        flash(f"no such product found: {store_name}/{product_name}")
        return redirect(url_for("buying.view_store", name=store_name))
    product = mathching[0]
    form = EditProductForm_one_field()
    error = None
    if form.validate_on_submit():
        field_to_change = form.field_to_change.data
        new_value = form.new_value.data
        if field_to_change == 'name':
            res = domain.edit_product_name(store_name, product_name, new_value)
        elif field_to_change == 'category':
            res = domain.edit_product_category(store_name, product_name, new_value)
        elif field_to_change == 'price':
            try:
                new_value = float(new_value)
            except ValueError:
                flash("Invalid value for price. Please enter a valid number.")
                return redirect(url_for("buying.view_store", name=store_name))
            res = domain.edit_product_price(store_name, product.price, new_value)
        elif field_to_change == 'quantity':
            try:
                new_value = int(new_value)
            except ValueError:
                flash("Invalid value for quantity. Please enter a valid integer.")
                return redirect(url_for("buying.view_store", name=store_name))
            res = domain.edit_product_quantity(store_name, product_name, new_value)
        if res.success:
            flash(f"You've change {product_name} {field_to_change} to {new_value}!", category="success")
            return redirect(url_for("buying.view_store", name=store_name))
        error = res.description
        flash(error, category="danger")
        return redirect(url_for("buying.view_store", name=store_name))
    return render_template("products/edit_product.html", form=form, error=error)


@bp.route('/products/<store_name>/<product_name>', methods=['GET'])
def product_page(store_name, product_name):
    domain = get_domain_adapter()
    store_response = domain.get_store(store_name)
    if not store_response.success:
        flash(store_response.description)
        return redirect(url_for('home.home'))
    mathching: List[ProductDto] = [p for p in store_response.result if p.name == product_name]
    if len(mathching) == 0:
        flash(f"no such product found: {store_name}/{product_name}")
        return redirect(url_for("buying.view_store", name=store_name))
    product = mathching[0]
    return render_template('products/product_page.html', product=product, store_name=store_name)


@bp.route('/start_bid/<store_name>/<product_name>', methods=['GET'])
def start_bid(store_name, product_name):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase policy rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.start_bid(store_name, product_name)
    if res.success:
        flash('started bid successfully')
    else:
        flash(res.description)

    return redirect(url_for("buying.view_store", name=store_name))