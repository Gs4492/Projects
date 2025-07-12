from flask import Blueprint, render_template, request, redirect, url_for
import requests

billing_bp = Blueprint('billing_bp', __name__)
API_URL = 'http://localhost:8000/invoices'

@billing_bp.route('/invoices')
def invoices():
    res = requests.get(API_URL)
    invoices = res.json() if res.status_code == 200 else []
    return render_template('invoices.html', invoices=invoices)

@billing_bp.route('/invoices/add', methods=['POST'])
def add_invoice():
    data = {
        'order_id': int(request.form['order_id']),
        'amount': float(request.form['amount']),
        'payment_status': request.form.get('payment_status', 'Unpaid')
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('billing_bp.invoices'))

@billing_bp.route('/invoices/pay/<int:id>')
def pay_invoice(id):
    requests.put(f"{API_URL}/{id}", json={'payment_status': 'Paid'})
    return redirect(url_for('billing_bp.invoices'))
