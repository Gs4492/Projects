from flask import Blueprint, render_template
from . import login_required

credit_management_bp = Blueprint('credit_management', __name__)

@credit_management_bp.route('/credit_management')
@login_required
def credit_management():
    return render_template('pages/credit_management.html')
