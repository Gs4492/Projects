from flask import Blueprint



auth_blueprint = Blueprint('auth', __name__, template_folder='../Web/templates')

from . import routes
