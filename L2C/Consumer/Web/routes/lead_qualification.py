import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash

lead_qualification_web_bp = Blueprint('lead_qualification_web', __name__)

API_URL = 'http://localhost:5011/qualified-leads'

@lead_qualification_web_bp.route('/lead-qualification', methods=['GET', 'POST'])
def lead_qualification():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'score': int(request.form['score']),
            'qualified': request.form.get('qualified', 'pending')
        }
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                flash('Lead qualified successfully!', 'success')
            else:
                flash('Error qualifying lead.', 'danger')
        except Exception as e:
            flash(f'Connection error: {e}', 'danger')
        return redirect(url_for('lead_qualification_web.lead_qualification'))

    # GET
    try:
        response = requests.get(API_URL)
        leads = response.json() if response.status_code == 200 else []
    except Exception:
        leads = []
        flash('Could not connect to LeadQualification service.', 'warning')

    return render_template('pages/lead_qualification.html', leads=leads)
