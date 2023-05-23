
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("buying", __name__)

@bp.get('/store/<name>')
def view_store(name: str):
    domain = get_domain_adapter()
    store = domain.get_store(name)
    return render_template("buying/view_store.html", products=store)
