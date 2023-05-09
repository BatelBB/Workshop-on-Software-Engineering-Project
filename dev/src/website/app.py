from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from core_features.nav import nav
from core_features.dicebear import dicebear_methods

from blueprints import auth

app = Flask(__name__)
Bootstrap(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

nav.init_app(app)
app.jinja_env.globals.update(**dicebear_methods, **wtforms_helpers)

print(app.jinja_env.globals)

@app.route("/")
def home():
    return render_template('home.html')


# app.register_blueprint(auth, '/auth')


if __name__ == '__main__':
    app.run(debug=True)
