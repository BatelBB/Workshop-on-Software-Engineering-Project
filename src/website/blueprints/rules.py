import validation
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, IntegerField
from wtforms.validators import Length, DataRequired, NumberRange

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("rules", __name__)

@bp.route('/rules_view/<store_name>', methods=('POST', 'GET'))
def rules_view(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase policy rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    purchase_rules = domain.get_purchase_rules(store_name)
    return render_template("selling/rules_view.html", rule_dict=purchase_rules, store_name=store_name)


@bp.route('/delete_rule/<store_name>/<int:index>', methods=['POST'])
def delete_rule(store_name, index):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase policy rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.delete_purchase_rule(index, store_name)

    flash('Rule deleted successfully')
    return redirect(url_for('rules.rules_view', store_name=store_name))

class AddSimpleRuleForm(FlaskForm):
    product_name = StringField(validators=[Length(min=3, max=100)])
    gle = StringField(validators=[DataRequired()])
    amount = IntegerField(validators=[NumberRange(min=0)])
    submit = SubmitField()

@bp.route('/add_simple_rule/<store_name>',  methods=('POST', 'GET'))
def add_simple_rule(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    form = AddSimpleRuleForm()
    if form.validate_on_submit():
        p_name = form.product_name.data
        gle = form.gle.data
        amount = form.amount.data
        msg = domain.add_simple_purchase_rule(store_name, p_name, gle, amount)
        flash(msg)
        return redirect(url_for('rules.rules_view', store_name=store_name))
    return render_template("selling/add_simple_rule.html", form=form)