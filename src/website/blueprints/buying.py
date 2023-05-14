from website.core_features.auth import get_domain_session, is_logged_in
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from website.core_features.auth import get_user


bp = Blueprint("buying", __name__)

@bp.get('/store/<name>')
def view_store(name: str):
    items = get_domain_session(session).get_store(name).result
    return render_template("buying/view_store.html", name=name, items=items)
