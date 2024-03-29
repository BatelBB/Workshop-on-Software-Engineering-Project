from typing import List

from wtforms import Form, StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from src.domain.main.Market.Permissions import Permission
from website.core_features.domain_access.market_access import get_domain_adapter
from website.core_features.domain_access.session_adapter_dto import ProductDto

bp = Blueprint("staff", __name__)


# appoint manager
class AppointmentForm(FlaskForm):
    appointee = SelectField('Select User', validators=[validation.DataRequired()], choices=[])
    submit = SubmitField()


@bp.route('/appoint_manager/<store_name>', methods=('POST', 'GET'))
def appoint_manager(store_name: str):
    domain = get_domain_adapter()
    all_users = domain.get_all_registered_users()
    if not domain.is_logged_in:
        flash("You tried to appoint a manager but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.AppointManager.name not in perms:
        flash("Not allowed to appoint manager to this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    form.appointee.choices = [(user, user) for user in all_users]
    if form.validate_on_submit():
        manager_name = form.appointee.data
        if domain.appoint_manager(store_name, manager_name):
            flash(f'{manager_name} is appointed manager of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
        else:
            flash(f"Couldn't appoint manager - {manager_name} isn't registered")
    return render_template("products/staff.html", form=form, get_all_registered_users=all_users, headline="Appoint Manager")


# appoint owner
@bp.route('/appoint_owner/<store_name>', methods=('POST', 'GET'))
def appoint_owner(store_name: str):
    domain = get_domain_adapter()
    all_users = domain.get_all_registered_users()
    if not domain.is_logged_in:
        flash("You tried to appoint an owner but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.AppointOwner.name not in perms:
        flash("Not allowed to appoint owner to this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    form.appointee.choices = [(user, user) for user in all_users]
    if form.validate_on_submit():
        owner_name = form.appointee.data
        if domain.appoint_owner(store_name, owner_name):
            flash(f'{owner_name} is appointed owner of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
        else:
            flash("Couldn't appoint owner")
    return render_template("products/staff.html", form=form, get_all_registered_users=all_users, headline="Appoint Owner")


# remove manager
@bp.route('/remove_manager/<store_name>', methods=('POST', 'GET'))
def remove_manager(store_name: str):
    domain = get_domain_adapter()
    all_users = domain.get_all_store_managers(store_name)
    if not domain.is_logged_in:
        flash("You tried to remove a manager but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.CancelManagerAppointment.name not in perms:
        flash("Not allowed to remove manager from this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    form.appointee.choices = [(user, user) for user in all_users]
    if form.validate_on_submit():
        manager_name = form.appointee.data
        if domain.remove_manager(store_name, manager_name):
            flash(f'{manager_name} is not appointed manager of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
        else:
            flash("Couldn't remove manager")
    return render_template("products/staff.html", form=form, get_all_registered_users=all_users, headline="Remove Manager")


@bp.route('/remove_owner/<store_name>', methods=('POST', 'GET'))
def remove_owner(store_name: str):
    domain = get_domain_adapter()
    all_users = domain.get_all_store_owners(store_name)
    if not domain.is_logged_in:
        flash("You tried to remove an owner but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    perms = {p.name for p in domain.permissions_of(store_name)}
    if Permission.CancelOwnerAppointment.name not in perms:
        flash("Not allowed to remove owner from this store")
        return redirect(url_for("buying.view_store", name=store_name))
    form = AppointmentForm()
    form.appointee.choices = [(user, user) for user in all_users]
    if form.validate_on_submit():
        owner_name = form.appointee.data
        if domain.remove_owner(store_name, owner_name).success:
            flash(f'{owner_name} is not appointed owner of {store_name}')
            return redirect(url_for("buying.view_store", name=store_name))
        else:
            flash("Couldn't remove owner")
    return render_template("products/staff.html", form=form, get_all_registered_users=all_users, headline="Remove Owner")


@bp.route('/view_staff_info/<store_name>', methods=('GET', 'POST'))
def view_staff_info(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to view staff info but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    staff = domain.get_store_staff_with_permission(store_name)
    form = AppointmentForm()
    form.appointee.choices = [(user, user) for user in staff.keys()]
    worker_permissions = None
    if form.validate_on_submit():
        worker = form.appointee.data
        worker_permissions = staff[worker]
    return render_template("products/staff_info.html", form=form, headline="View Staff Info", permissions=worker_permissions)

