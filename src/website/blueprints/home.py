import website.compatability_patch
from flask import Flask, flash, session, url_for, Blueprint
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from src.domain.main.Utils.Response import Response
from website.blueprints.auth import bp as auth
#from website.blueprints.selling import bp as selling
from website.blueprints.buying import bp as buying
from website.core_features.domain_access.market_access import get_domain_adapter

from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    domain = get_domain_adapter()
    stores_result = domain.get_stores()  # TODO get_domain_session(session).get_all_stores().result
    from random import shuffle
    made_by = ['Batel', 'Hagai', 'Mendi', 'Nir', 'Yuval']
    permissions = {p.name for p in domain.get_admin_permissions()}
    shuffle(made_by)
    if stores_result.success:
        stores = stores_result.result
    else:
        flash('Error in finding stores: ' + stores_result.description, "danger")
        stores = []
    if domain.is_logged_in:
        your_stores_result = domain.your_stores()
        if isinstance(your_stores_result, Response):
            if not your_stores_result.success:
                flash("Couldn't find which stores are yours: " + your_stores_result.description, "danger")
                your_stores = []
            else:
                your_stores = your_stores_result.result
        else:
            your_stores = your_stores_result
    else:
        your_stores = []
    return render_template('home.html', made_by=made_by, stores=stores, your_stores=your_stores, permissions=permissions)

