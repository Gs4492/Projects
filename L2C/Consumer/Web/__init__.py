import os
from flask import Flask
from flask_cors import CORS
from Consumer.Web.config import Config
from Consumer.Web.routes import all_blueprints
from Infrastructure.Auth.auth import auth_blueprint

def create_app():
    # Absolute path to the folder where this file (create_app) lives
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Join it to get the templates and static folders correctly
    template_dir = os.path.join(base_dir, 'templates')

    static_dir = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']

    CORS(app)

    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    for bp in all_blueprints:
        app.register_blueprint(bp)

    return app
