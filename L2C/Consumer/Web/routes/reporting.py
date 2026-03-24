from flask import Blueprint, render_template
from . import login_required

reporting_bp = Blueprint('reporting', __name__)

@reporting_bp.route('/reporting')
@login_required
def reporting():
    return render_template('pages/reporting.html')
