from flask import Blueprint, flash, redirect, url_for, render_template

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("rules", __name__)

@bp.route('/rules_view/<store_name>', methods=('POST', 'GET'))
def rules_view(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage purchase policy rules but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    return render_template("selling/rules_view.html", rules = domain.get_purchase_rules(store_name))
