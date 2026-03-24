from flask import Flask, render_template
from Infrastructure.Auth.Web.config import Config
from Infrastructure.Auth.auth import auth_blueprint
from Infrastructure.Auth.dal import init_db
import os


def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Infrastructure/Auth/Web/templates'))


    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    app.register_blueprint(auth_blueprint, url_prefix='/')


    @app.route('/')
    def home():
        return render_template('login.html')  # or dashboard.html


    init_db(app)  # Initialize database if needed
    return app
