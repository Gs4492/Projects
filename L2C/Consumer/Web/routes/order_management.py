from flask import Blueprint, render_template
from . import login_required

order_management_bp = Blueprint('order_management', __name__)

@order_management_bp.route('/order_management')
@login_required
def order_management():
    return render_template('pages/order_management.html')
