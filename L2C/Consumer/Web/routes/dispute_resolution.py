from flask import Blueprint, render_template
from . import login_required

dispute_resolution_bp = Blueprint('dispute_resolution', __name__)

@dispute_resolution_bp.route('/dispute_resolution')
@login_required
def dispute_resolution():
    return render_template('pages/dispute_resolution.html')
