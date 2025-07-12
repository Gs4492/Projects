from flask import Blueprint, render_template, request, redirect, url_for
import requests

customer_bp = Blueprint('customer_bp', __name__)
API_URL = 'http://localhost:8000/customers'

@customer_bp.route('/customers')
def customers():
    res = requests.get(API_URL)
    customers = res.json() if res.status_code == 200 else []
    return render_template('customers.html', customers=customers)

@customer_bp.route('/customers/add', methods=['POST'])
def add_customer():
    data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'phone': request.form.get('phone', ''),
        'address': request.form.get('address', ''),
        'preferences': request.form.get('preferences', '')
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('customer_bp.customers'))

@customer_bp.route('/customers/delete/<int:id>')
def delete_customer(id):
    requests.delete(f"{API_URL}/{id}")
    return redirect(url_for('customer_bp.customers'))
