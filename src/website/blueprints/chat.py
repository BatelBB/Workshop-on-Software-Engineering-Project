
from flask import flash, Blueprint
bp = Blueprint("chat", __name__)

@bp.route('/inbox')
def inbox():
    return 'WIP'
