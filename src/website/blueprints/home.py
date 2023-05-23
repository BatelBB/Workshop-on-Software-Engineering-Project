import website.compatability_patch
from flask import Flask, flash, session, url_for, Blueprint
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from domain.main.Utils.Response import Response, BusinessLayerException
from website.blueprints.auth import bp as auth
from website.blueprints.selling import bp as selling
from website.blueprints.buying import bp as buying
from website.core_features.domain_access.market_access import get_domain_adapter

from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    domain = get_domain_adapter()

    try:
        stores = domain.get_stores()
    except BusinessLayerException as e:
        flash(f'Error in finding stores: {e}', "danger")
        stores = []

    if domain.is_logged_in:
        try:
            your_stores = domain.your_stores()
        except BusinessLayerException as e:
            flash(f"error in finding your stores: {e}", "danger")
            your_stores = []
    else:
        your_stores = []

    from random import shuffle
    made_by = ['Batel', 'Hagai', 'Mendi', 'Nir', 'Yuval']
    shuffle(made_by)

    return render_template('home.html',
                           made_by=made_by,
                           stores=stores,
                           your_stores=your_stores,
                           username=domain.username)

