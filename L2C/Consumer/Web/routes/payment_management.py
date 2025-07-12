from flask import Blueprint, render_template
from . import login_required

payment_management_bp = Blueprint('payment_management', __name__)

@payment_management_bp.route('/payment_management')
@login_required
def payment_management():
    return render_template('pages/payment_management.html')
