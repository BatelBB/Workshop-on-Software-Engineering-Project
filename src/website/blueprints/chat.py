
from flask import flash, Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("chat", __name__)


@bp.route('/inbox')
def inbox():
    domain = get_domain_adapter()

    if not domain.is_logged_in:
        flash('Must be logged in to chat.')
        return redirect(url_for('home.home'))

    return render_template('chat/inbox.html')


@bp.route('/chat/<username>')
def chat(username: str):
    domain = get_domain_adapter()

    if not domain.is_logged_in:
        flash('Must be logged in to chat.')
        return redirect(url_for('home.home'))

    if username not in domain.get_all_registered_users():
        flash(f"Can't chat with {username}. There is no such user.", category='danger')
        return redirect(url_for('home.home'))
    return render_template('chat/chat.html', username=username)


class StartChatForm(FlaskForm):
    username = SelectField(label='Username')
    submit = SubmitField()


@bp.route('/start_chat', methods=('GET', 'POST'))
def start_chat():
    domain = get_domain_adapter()

    if not domain.is_logged_in:
        flash('Must be logged in to chat.')
        return redirect(url_for('home.home'))

    form = StartChatForm()
    domain = get_domain_adapter()
    usernames = list(domain.get_all_registered_users())
    form.username.choices = usernames

    # from domain.main.Chat.chat_controller import NOREPLY_USERNAME
    # usernames.remove(NOREPLY_USERNAME)
    # usernames.remove(domain.username)

    if form.validate_on_submit():
        username = form.username.data
        if username not in usernames:
            form.username.errors.append("There is no such user.")
        else:
            return redirect(url_for('chat.chat', username=username))

    return render_template('chat/start_chat.html', form=form)