from typing import List

from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter
from website.core_features.domain_access.session_adapter_dto import ProductDto

bp = Blueprint("staff", __name__)


# appoint manager
class AppointManagerForm(FlaskForm):
    manager_name = StringField(validators=[validation.Length(min=3, max=100)])
    submit = SubmitField()
@bp.route('/appoint_manager/<store_name>', methods=('POST', 'GET'))
def appoint_manager(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to appoint a manager but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.AppointManager.name not in perms:
        flash("Not allowed to appoint manager to this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointManagerForm()
    if form.validate_on_submit():
        manager_name = form.manager_name.data
        if not domain.appoint_manager(store_name, manager_name):
            flash("Couldn't appoint manager")
        else:
            flash(f'{manager_name} is appointed manager of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
    return render_template("selling/staff.html", form=form)
# appoint owner

# remove manager

# remove owner
