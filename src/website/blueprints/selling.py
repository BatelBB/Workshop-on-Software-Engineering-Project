from website.core_features.auth import get_domain_session, is_logged_in
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import wtforms.validators as validation
from flask import Blueprint, flash, redirect, render_template, session, url_for

from website.core_features.auth import get_user


bp = Blueprint("selling", __name__)

class CreateStoreForm(FlaskForm):
    name = StringField(validators=[validation.DataRequired()])
    submit = SubmitField()


@bp.route('/create_store', methods=('GET', 'POST'))
def create_store():
    if not is_logged_in(session):
        flash("You tried to create a store, but you need to be logged in for that.")
        return redirect(url_for('home'))
    
    form = CreateStoreForm()
    error = None
    if form.validate_on_submit():
        domain_session = get_domain_session(session)
        store_name = form.name.data
        res = domain_session.open_store(store_name)
        if res.success:
            flash(f"You've created a store {store_name}. Here's hoping bussiness goes well!", category="success")
            return redirect(url_for("home"))
        error = res.description
        flash(error, category="danger")
    return render_template("selling/create_store.html", form=form, error=error)