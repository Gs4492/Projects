# routes/billing_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import requests

billing_bp = Blueprint('billing', __name__)
API_URL = 'http://localhost:8000/api/invoices'

@billing_bp.route('/billing')
def list_bills():
    res = requests.get(API_URL)
    return render_template('billing.html', invoices=res.json())

@billing_bp.route('/billing/add', methods=['POST'])
def add_invoice():
    data = {
        "patient_name": request.form['patient_name'],
        "amount": request.form['amount'],
        "status": request.form['status'],
        "date": request.form['date']
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('billing.list_bills'))

@billing_bp.route('/billing/edit/<int:invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    if request.method == 'POST':
        updated_data = {
            "patient_name": request.form['patient_name'],
            "amount": request.form['amount'],
            "status": request.form['status'],
            "date": request.form['date']
        }
        requests.put(f'http://localhost:8000/api/invoices/{invoice_id}', json=updated_data)
        return redirect(url_for('billing.list_invoices'))

    res = requests.get(f'http://localhost:8000/api/invoices/{invoice_id}')
    if res.status_code == 200:
        invoice = res.json()
        return render_template('invoices_edit.html', invoice=invoice)
    else:
        return f"Invoice with ID {invoice_id} not found", 404


@billing_bp.route('/billing/delete/<int:invoice_id>')
def delete_invoice(invoice_id):
    requests.delete(f'{API_URL}/{invoice_id}')
    return redirect(url_for('billing.list_bills'))
