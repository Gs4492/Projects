from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from . import login_required

lead_generation_bp = Blueprint('lead_generation', __name__)
API_URL = 'http://localhost:5010/leads'

@lead_generation_bp.route('/lead_generation', methods=['GET', 'POST'])
@login_required
def lead_generation():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'source': request.form.get('source', 'Website')
        }
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                flash('Lead submitted successfully!', 'success')
                return redirect(url_for('lead_generation.lead_generation'))
            else:
                flash('Failed to submit lead', 'danger')
        except:
            flash('Could not connect to LeadGeneration service.', 'danger')

    try:
        leads = requests.get(API_URL).json()
    except:
        leads = []
    return render_template('pages/lead_generation.html', leads=leads)
