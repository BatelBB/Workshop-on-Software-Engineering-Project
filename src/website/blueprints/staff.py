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
class AppointmentForm(FlaskForm):
    appointee = StringField(validators=[validation.Length(min=3, max=100)])
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
    form = AppointmentForm()
    if form.validate_on_submit():
        manager_name = form.appointee.data
        if not domain.appoint_manager(store_name, manager_name):
            flash("Couldn't appoint manager")
        else:
            flash(f'{manager_name} is appointed manager of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
    return render_template("selling/staff.html", form=form)

# appoint owner
@bp.route('/appoint_owner/<store_name>', methods=('POST', 'GET'))
def appoint_owner(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to appoint an owner but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.AppointOwner.name not in perms:
        flash("Not allowed to appoint owner to this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    if form.validate_on_submit():
        owner_name = form.appointee.data
        if not domain.appoint_owner(store_name, owner_name):
            flash("Couldn't appoint owner")
        else:
            flash(f'{owner_name} is appointed owner of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
    return render_template("selling/staff.html", form=form)
# remove manager
@bp.route('/remove_manager/<store_name>', methods=('POST', 'GET'))
def remove_manager(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to remove a manager but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.CancelManagerAppointment.name not in perms:
        flash("Not allowed to remove manager from this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    if form.validate_on_submit():
        manager_name = form.appointee.data
        if not domain.remove_manager(store_name, manager_name):
            flash("Couldn't remove manager")
        else:
            flash(f'{manager_name} is not appointed manager of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
    return render_template("selling/staff.html", form=form)

@bp.route('/remove_owner/<store_name>', methods=('POST', 'GET'))
def remove_owner(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to remove an owner but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.CancelOwnerAppointment.name not in perms:
        flash("Not allowed to remove owner from this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    if form.validate_on_submit():
        owner_name = form.appointee.data
        if not domain.remove_owner(store_name, owner_name):
            flash("Couldn't remove owner")
        else:
            flash(f'{owner_name} is not appointed owner of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
    return render_template("selling/staff.html", form=form)
# remove owner
