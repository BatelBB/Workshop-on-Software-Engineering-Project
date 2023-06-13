import wtforms as wtf
import wtforms.validators as validation
from flask import flash, url_for, Blueprint, redirect
from flask import render_template
from flask_wtf import FlaskForm

# from website.blueprints.selling import bp as selling
from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("dms", __name__)


@bp.route("/inbox")
def inbox():
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("guest can't access inbox")
        return redirect(url_for("home.home"))
    res = domain.get_inbox()
    if not res.success:
        flash(res.description)
        return redirect(url_for("home.home"))
    counts = {True: 0, False: 0}
    for n in res.result:
        counts[n.seen] += 1
    return render_template("dms/inbox.html", inbox=res.result, read=counts[True], unread=counts[False])


class SendMessageForm(FlaskForm):
    recipient = wtf.SelectField(label="recipient")
    message = wtf.TextAreaField(label="message", validators=[validation.DataRequired()])
    submit = wtf.SubmitField(label="submit")


@bp.route("/send_message", methods=('POST', 'GET'))
def send_message():
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("only logged in users may send messages", category='danger')
        return redirect(url_for('home.home'))
    form = SendMessageForm()
    form.recipient.choices = [u for u in domain.get_all_registered_users()]

    if form.validate_on_submit():
        res = domain.send_message(form.recipient.data, form.message.data)
        if res.success:
            flash(f"message to {form.recipient.data} sent successfully")
            return redirect(url_for("dms.inbox"))
        flash(res.description)
    return render_template("dms/send_message.html", form=form)


@bp.route("/mark_read/<int:msg_id>")
def mark_read(msg_id: int):
    domain = get_domain_adapter()
    res = domain.mark_read(msg_id)
    if not res.success:
        flash(res.description, category="danger")
    return redirect(url_for("dms.inbox"))
