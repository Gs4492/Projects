from flask import Blueprint, render_template
from . import login_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    return render_template('pages/analytics.html')
