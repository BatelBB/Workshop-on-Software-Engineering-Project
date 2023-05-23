import website.compatability_patch
from flask import Flask, flash, session, url_for
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from domain.main.Utils.Response import Response, BusinessLayerException
from website.blueprints.auth import bp as auth
from website.blueprints.selling import bp as selling
from website.blueprints.buying import bp as buying
from website.blueprints.home import bp as home

from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

from jinja2.filters import do_mark_safe

# from blueprints import auth

app = Flask(__name__)
Bootstrap(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

nav.init_app(app)

app.jinja_env.globals.update(**dicebear_methods)


def jinja_render(*args, **kwargs):
    return do_mark_safe(render_template(*args, **kwargs))


app.jinja_env.globals.update(render_template=jinja_render)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(selling)
app.register_blueprint(buying)

@app.errorhandler(500)
def on_error(e):
    return render_template("500.html", error=e.original_exception)

if __name__ == '__main__':
    app.run(debug=True)
