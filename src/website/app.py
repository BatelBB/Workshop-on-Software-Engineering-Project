import website.compatability_patch
from flask import Flask, flash, session, url_for
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from domain.main.Utils.Response import Response
from website.blueprints.auth import bp as auth
from website.blueprints.selling import bp as selling
from website.blueprints.buying import bp as buying
from website.blueprints.home import bp as home

from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

# from blueprints import auth

app = Flask(__name__)
Bootstrap(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

nav.init_app(app)

app.jinja_env.globals.update(**dicebear_methods)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(selling)
app.register_blueprint(buying)


if __name__ == '__main__':
    app.run(debug=True)
