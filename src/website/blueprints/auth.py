from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("auth", __name__)


class RegisterForm(FlaskForm):
    username = StringField(validators=[validation.Length(min=2, max=20)])
    password = PasswordField(validators=[validation.Length(min=2)])
    repeat_password = PasswordField(label="repeat password", validators=[validation.EqualTo("password")])
    submit = SubmitField()


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        domain = get_domain_adapter()
        res = domain.register(form.username.data, form.password.data)
        if res.success:
            return redirect(url_for("home.home"))
        error = str(res.description)
        flash(error, category="danger")
    print('form error', form.errors)
    return render_template("auth/register.html", form=form, error=error)


class LoginForm(FlaskForm):
    username = StringField(validators=[validation.Length(min=2, max=20)])
    password = PasswordField(validators=[validation.Length(min=2)])
    submit = SubmitField()


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        username = form.username.data
        domain = get_domain_adapter()
        res = domain.login(username, form.password.data)
        if res.success:
            flash(f"welcome, {username}", category="success")
            return redirect(url_for("home.home"))
        error = str(res.description)
        flash(error, category="danger")
    return render_template("auth/login.html", form=form, error=error)


@bp.route("/logout")
def logout():
    response = get_domain_adapter().logout()
    if response.success and response.success:
        flash("You're now logged out.", category="success")
    else:
        flash("Couldn't log out: " + response.description, category="danger")
    return redirect(url_for("home.home"))
