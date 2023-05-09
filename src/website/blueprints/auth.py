from website.core_features.auth import get_domain_session
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from website.core_features.auth import get_user


bp = Blueprint("auth", __name__)


class RegisterForm(FlaskForm):
    username = StringField(validators=[validation.Length(min=5, max=20)])
    password = PasswordField(validators=[validation.Length(min=4)])
    repeat_password = PasswordField(label="repeat password", validators=[validation.EqualTo("password")])
    submit = SubmitField()

@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm() 
    error = None
    if form.validate_on_submit():
        domain_session = get_domain_session(session)
        res = domain_session.register(form.username.data, form.password.data)
        if res.success:
            return redirect(url_for("home"))
        error = str(res.description)
        flash(error, category="danger")
    print('form errosr', form.errors)
    return render_template("auth/register.html", form=form, error=error)


class LoginForm(FlaskForm):
    username = StringField(validators=[validation.Length(min=5, max=20)])
    password = PasswordField(validators=[validation.Length(min=4)])
    submit = SubmitField()

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm() 
    error = None
    if form.validate_on_submit():
        username = form.username.data
        domain_session = get_domain_session(session)
        res = domain_session.login(username, form.password.data)
        if res.success:
            flash(f"welcome, {username}", category="success")
            session["username"] = username
            return redirect(url_for("home"))
        error =  str(res.description)
        flash(error, category="danger")
    return render_template("auth/login.html", form=form, error=error)

