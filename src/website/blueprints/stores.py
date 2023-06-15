# Blueprint for creating, updating, opening, closing and deleting stores.
# Not including staff, products.

from typing import List

from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from src.domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter
from website.core_features.domain_access.session_adapter_dto import ProductDto

bp = Blueprint("stores", __name__)


class CreateStoreForm(FlaskForm):
    name = StringField(validators=[validation.DataRequired()])
    submit = SubmitField()


class RemoveStoreForm(FlaskForm):
    store = SelectField('Select a store to remove:', validators=[validation.DataRequired()])
    submit = SubmitField('Remove Store')


class ReopenStoreForm(FlaskForm):
    store = SelectField('Select a store to reopen:', validators=[validation.DataRequired()])
    submit = SubmitField('Reopen Store')


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
    return render_template("stores/create_store.html", form=form, error=error)


# remove store
@bp.route('/remove_store', methods=('GET', 'POST', 'DELETE'))
def remove_store():
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to remove a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    stores = domain.get_stores()
    form = RemoveStoreForm()
    form.store.choices = [store.name for store in stores.result]
    error = None
    if form.validate_on_submit():
        store_name = form.store.data
        res = domain.remove_store(store_name)
        if res.success:
            flash(f"You've removed {store_name}.", category="success")
            return redirect(url_for("home.home"))
        error = res.description
        flash(error, category="danger")
    return render_template("stores/remove_store.html", form=form, error=error)


# reopen store
@bp.route('/reopen_store', methods=('GET', 'POST'))
def reopen_store():
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to reopen a store, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    stores = domain.get_deleted_stores()
    form = ReopenStoreForm()
    form.store.choices = [store.name for store in stores.result]
    error = None
    if form.validate_on_submit():
        store_name = form.store.data
        res = domain.open_store(store_name)
        if res.success:
            flash(f"You've reopened a store {store_name}. Here's hoping bussiness goes well!", category="success")
            return redirect(url_for("home.home"))
        error = res.description
        flash(error, category="danger")
    return render_template("stores/remove_store.html", form=form, error=error)

@bp.route('/view_purchase_history/<store_name>', methods=('GET', 'POST'))
def view_purchase_history_owner(store_name: str):
    domain = get_domain_adapter()
    permissions = {p.name for p in domain.permissions_of(store_name)}
    if not domain.is_logged_in:
        flash("You tried to view purchase_history, but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    purchase_history = domain.get_purchase_history_owner(store_name)
    return render_template("stores/view_purchase_history.html", purchase_history=purchase_history, permissions=permissions)

@bp.route('/view_purchase_history', methods=('GET', 'POST'))
def view_purchase_history_admin():
    domain = get_domain_adapter()
    if not domain.is_admin():
        flash("Get out of here, you are NOT an admin!!!!!!!")
        return redirect(url_for("home.home"))
    # get all stores
    all_stores = domain.get_stores().result
    #go through all stores and add to dictionary with the output of get all stores from session adapter
    purchase_history_for_all_stores = {}
    for store in all_stores:
        purchase_history_for_all_stores[store.name] = domain.get_purchase_history_owner(store.name)
    return render_template("partials/view_purchase_history_admin.html", purchase_history=purchase_history_for_all_stores)
