from flask import Blueprint, render_template
from . import login_required

cash_application_bp = Blueprint('cash_application', __name__)

@cash_application_bp.route('/cash_application')
@login_required
def cash_application():
    return render_template('pages/cash_application.html')
