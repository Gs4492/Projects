# routes/staff_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import requests

staff_bp = Blueprint('staff', __name__)
API_URL = 'http://localhost:8000/api/staff'

@staff_bp.route('/staff')
def list_staff():
    res = requests.get(API_URL)
    return render_template('staff.html', staff=res.json())

@staff_bp.route('/staff/add', methods=['POST'])
def add_staff():
    data = {
        "name": request.form['name'],
        "role": request.form['role'],
        "contact": request.form['contact'],
        "active": int(request.form.get('active', 1))
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('staff.list_staff'))

@staff_bp.route('/staff/delete/<int:staff_id>')
def delete_staff(staff_id):
    requests.delete(f'{API_URL}/{staff_id}')
    return redirect(url_for('staff.list_staff'))
