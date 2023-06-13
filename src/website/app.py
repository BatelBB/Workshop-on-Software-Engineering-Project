import website.compatability_patch
from flask import Flask, flash, session, url_for
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from src.domain.main.Utils.Response import Response
from website.blueprints.searching import bp as searching
from website.blueprints.discounts import bp as discounts
from website.blueprints.rules import bp as rules
from src.domain.main.Market.Permissions import Permission
from src.domain.main.Utils.Response import Response
from website.blueprints.auth import bp as auth
from website.blueprints.buying import bp as buying
from website.blueprints.home import bp as home
from website.blueprints.products import bp as products
from website.blueprints.stores import bp as stores
from website.blueprints.staff import bp as staff
from website.blueprints.dms import bp as dms
from website.core_features.domain_access.market_access import get_domain_adapter

from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

# from blueprints import auth
from website.core_features.realtime.realtime import init_realtime

app = Flask(__name__)
Bootstrap(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SECRET_KEY"] = app.secret_key

nav.init_app(app)

app.jinja_env.globals.update(**dicebear_methods)
app.jinja_env.globals.update(Permission=Permission)

def get_username():
    return get_domain_adapter().username


def is_logged_in():
    return get_domain_adapter().is_logged_in


app.jinja_env.globals.update(get_username=get_username, is_logged_in=is_logged_in)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(stores)
app.register_blueprint(staff)
app.register_blueprint(products)
app.register_blueprint(buying)
app.register_blueprint(rules)
app.register_blueprint(discounts)
app.register_blueprint(searching)
app.register_blueprint(dms)


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


socketio = init_realtime(app)



def start_app():
    print('start_app')
    socketio.run(app, port=80)
