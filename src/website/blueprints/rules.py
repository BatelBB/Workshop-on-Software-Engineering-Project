from flask import Blueprint, flash, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, IntegerField, FloatField
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
    return render_template("products/rules_view.html", rule_dict=purchase_rules, store_name=store_name)


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
    return render_template("products/add_simple_rule.html", form=form)

class AddComplexRuleForm(FlaskForm):
    product1_name = StringField(validators=[Length(min=3, max=100)])
    gle1 = StringField(validators=[DataRequired()])
    amount1 = IntegerField(validators=[NumberRange(min=0)])
    product2_name = StringField(validators=[Length(min=3, max=100)])
    gle2 = StringField(validators=[DataRequired()])
    amount2 = IntegerField(validators=[NumberRange(min=0)])
    rule_type = SelectField('Rule Type', choices=[('and', 'AND'), ('or', 'OR')])
    submit = SubmitField()

@bp.route('/add_complex_rule/<store_name>',  methods=('POST', 'GET'))
def add_complex_rule(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    form = AddComplexRuleForm()
    if form.validate_on_submit():
        p1_name = form.product1_name.data
        gle1 = form.gle1.data
        amount1 = form.amount1.data
        p2_name = form.product1_name.data
        gle2 = form.gle1.data
        amount2 = form.amount1.data
        rule_type = form.rule_type.data
        msg = domain.add_complex_purchase_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2, rule_type)
        flash(msg)
        return redirect(url_for('rules.rules_view', store_name=store_name))
    return render_template("products/add_complex_rule.html", form=form)

class AddBasketRuleForm(FlaskForm):
    min_price = FloatField(validators=[NumberRange(min=0)])
    submit = SubmitField()

@bp.route('/add_basket_rule/<store_name>',  methods=('POST', 'GET'))
def add_basket_rule(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    form = AddBasketRuleForm()
    if form.validate_on_submit():
        min_price = form.min_price.data
        msg = domain.add_basket_purchase_rule(store_name, min_price)
        flash(msg)
        return redirect(url_for('rules.rules_view', store_name=store_name))
    return render_template("products/add_basket_rule.html", form=form)