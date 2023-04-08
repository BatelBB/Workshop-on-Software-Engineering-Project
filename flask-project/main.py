from flask import Flask
from random import randint

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "'Hello World’"


if __name__ == '__main__':
    app.run(debug=True)
