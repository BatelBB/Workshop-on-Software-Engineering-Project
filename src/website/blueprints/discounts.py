from flask import flash, redirect, url_for, render_template, Blueprint
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import NumberRange, Length, DataRequired, Optional

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("discounts", __name__)


@bp.route('/discounts_view/<store_name>', methods=('POST', 'GET'))
def discounts_view(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage discounts but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    discounts = domain.get_discounts(store_name)
    if discounts is None:
        discounts = {}
    return render_template("products/discounts_view.html", discounts_dict=discounts, store_name=store_name)
    # else:
    #     return redirect(url_for("buying.view_store", name=store_name))


@bp.route('/delete_discount/<store_name>/<int:index>', methods=['POST'])
def delete_discount(store_name, index):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage discounts but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.delete_discount(store_name, index)

    flash(res)
    return redirect(url_for('discounts.discounts_view', store_name=store_name))


class AddDiscount(FlaskForm):
    discount_type = SelectField('Discount Type',
                                choices=[('store', 'STORE'), ('product', 'PRODUCT'), ('category', 'CATEGORY')])
    percent = IntegerField(validators=[Optional(), NumberRange(min=0, max=100)])
    discount_for_name = StringField(validators=[Optional(), Length(min=1, max=100)])
    rule_type = SelectField('Rule Type', choices=[("None", "NONE"), ('and', 'AND'), ('or', 'OR'), ('basket', 'BASKET'), ('cond', 'COND')],
                            default=None)
    min_price = IntegerField(validators=[Optional(), NumberRange(min=0)])
    product1_name = StringField(validators=[Optional(), Length(min=1, max=100)])
    gle1 = StringField(validators=[Optional()])
    amount1 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    product2_name = StringField(validators=[Optional(), Length(min=1, max=100)])
    gle2 = StringField(validators=[Optional()])
    amount2 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField()


@bp.route('/add_discount/<store_name>', methods=('POST', 'GET'))
def add_discount(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to add a discount but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    form = AddDiscount()
    if form.validate_on_submit():
        discount_type = form.discount_type.data
        percent = form.percent.data
        discount_for_name = form.discount_for_name.data
        rule_type = form.rule_type.data
        min_price = form.min_price.data
        product1_name = form.product1_name.data
        gle1 = form.gle1.data
        amount1 = form.amount1.data
        product2_name = form.product2_name.data
        gle2 = form.gle2.data
        amount2 = form.amount2.data

        msg = domain.add_simple_discount(store_name, discount_type, percent,
                                         discount_for_name, rule_type,
                                         min_price, product1_name, gle1, amount1, product2_name,
                                         gle2, amount2)
        flash(msg)
        return redirect(url_for('discounts.discounts_view', store_name=store_name))
    return render_template("products/add_discount.html", form=form)


class ConnectDiscounts(FlaskForm):
    id1 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    id2 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    connection_type = SelectField('Connection Type',
                                  choices=[('and', 'AND'), ('or', 'OR'), ('max', 'MAX'), ('xor', 'XOR')], default=None)
    rule_type = SelectField('Rule Type', choices=[("None", "NONE"), ('and', 'AND'), ('or', 'OR'), ('basket', 'BASKET')],
                            default=None)
    min_price = IntegerField(validators=[Optional(), NumberRange(min=0)])
    product1_name = StringField(validators=[Optional(), Length(min=1, max=100)])
    gle1 = StringField(validators=[Optional()])
    amount1 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    product2_name = StringField(validators=[Optional(), Length(min=1, max=100)])
    gle2 = StringField(validators=[Optional()])
    amount2 = IntegerField(validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField()


@bp.route('/connect_discounts/<store_name>', methods=('POST', 'GET'))
def connect_discounts(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to connect discounts but you need to be logged in for that.")
        return redirect(url_for('home.home'))
    form = ConnectDiscounts()
    if form.validate_on_submit():
        id1 = form.id1.data
        id2 = form.id2.data
        connection_type = form.connection_type.data
        rule_type = form.rule_type.data
        min_price = form.min_price.data
        product1_name = form.product1_name.data
        gle1 = form.gle1.data
        amount1 = form.amount1.data
        product2_name = form.product2_name.data
        gle2 = form.gle2.data
        amount2 = form.amount2.data

        msg = domain.connect_discounts(store_name, id1, id2,
                                       connection_type, rule_type,
                                       min_price, product1_name, gle1, amount1, product2_name,
                                       gle2, amount2)
        flash(msg)
        return redirect(url_for('discounts.discounts_view', store_name=store_name))
    return render_template("products/connect_discounts.html", form=form)
