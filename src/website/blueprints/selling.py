from flask_restful.representations import json
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for, abort

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


@bp.route('/manage/<name>')
def manage(name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("can't manage store when not logged in")
        return redirect(url_for("home.home"))
    store = domain.get_store(name)
    permissions = domain.get_permissions(domain.username, name)
    if len(permissions) == 0:
        return abort()
    return [str(perm) for perm in permissions]


