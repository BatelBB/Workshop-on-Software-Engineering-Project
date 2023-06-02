# Blueprint for creating, updating, opening, closing and deleting stores.
# Not including staff, products.

from typing import List

from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from domain.main.Market.Permissions import Permission
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
    return render_template("selling/create_store.html", form=form, error=error)


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
    return render_template("selling/remove_store.html", form=form, error=error)


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
    return render_template("selling/remove_store.html", form=form, error=error)
