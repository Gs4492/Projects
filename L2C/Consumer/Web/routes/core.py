from flask import Blueprint, app, render_template
from . import login_required
import os
from flask import current_app

core_bp = Blueprint('core', __name__)

@core_bp.route('/')
@login_required
def home():
    return render_template('pages/L2C.html')

@core_bp.route('/test')
def test_template_path():
    full_path = os.path.join(current_app.template_folder, 'pages', 'L2C.html')
    exists = os.path.exists(full_path)
    return f"Exists: {exists}, Path: {full_path}"
