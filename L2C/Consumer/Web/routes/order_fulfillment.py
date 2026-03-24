from flask import Blueprint, render_template
from . import login_required

order_fulfillment_bp = Blueprint('order_fulfillment', __name__)

@order_fulfillment_bp.route('/order_fulfillment')
@login_required
def order_fulfillment():
    return render_template('pages/order_fulfillment.html')
