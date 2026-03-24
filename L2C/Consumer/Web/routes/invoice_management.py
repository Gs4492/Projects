from flask import Blueprint, render_template
from . import login_required

invoice_management_bp = Blueprint('invoice_management', __name__)

@invoice_management_bp.route('/invoice_management')
@login_required
def invoice_management():
    return render_template('pages/invoice_management.html')
