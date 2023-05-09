import website.compatability_patch
from flask import Flask, flash, session, url_for
import wtforms as wtf
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from website.blueprints.auth import bp as auth
from website.blueprints.selling import bp as selling
from website.blueprints.buying import bp as buying

from website.core_features.auth import get_domain_session, get_market
from website.core_features.nav import nav
from website.core_features.dicebear import dicebear_methods

# from blueprints import auth

app = Flask(__name__)
Bootstrap(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

nav.init_app(app)

app.jinja_env.globals.update(**dicebear_methods)

app.register_blueprint(auth)
app.register_blueprint(selling)
app.register_blueprint(buying)

@app.route("/")
def home():
    stores = get_domain_session(session).get_all_stores().result
    print('\n\nstores', stores)
    from random import shuffle
    made_by = ['Batel', 'Hagai', 'Mendi', 'Nir', 'Yuval']
    shuffle(made_by)
    return render_template('home.html', made_by=made_by, stores=stores)



if __name__ == '__main__':
    app.run(debug=True)
