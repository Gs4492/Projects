from flask import Blueprint, render_template, request, redirect, url_for
import requests

order_bp = Blueprint('order_bp', __name__)
API_URL = 'http://localhost:8000/orders'

@order_bp.route('/orders')
def orders():
    res = requests.get(API_URL)
    orders = res.json() if res.status_code == 200 else []
    return render_template('orders.html', orders=orders)

@order_bp.route('/orders/add', methods=['POST'])
def add_order():
    data = {
        'customer_name': request.form['customer_name'],
        'plant_name': request.form['plant_name'],
        'quantity': int(request.form['quantity']),
        'total_price': float(request.form['total_price'])
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('order_bp.orders'))

@order_bp.route('/orders/delete/<int:id>')
def delete_order(id):
    requests.delete(f"{API_URL}/{id}")
    return redirect(url_for('order_bp.orders'))
