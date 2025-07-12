from functools import wraps
from flask import session, redirect, url_for

# Common login_required decorator
def login_required(route_function):
    @wraps(route_function)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return route_function(*args, **kwargs)
    return wrapped

# Import all your blueprints
from .core import core_bp
from .order_management import order_management_bp
from .credit_management import credit_management_bp
from .payment_management import payment_management_bp
from .order_fulfillment import order_fulfillment_bp
from .reports import reports_bp
from .invoice_management import invoice_management_bp
from .dispute_resolution import dispute_resolution_bp
from .reporting import reporting_bp
from .cash_application import cash_application_bp
from .analytics import analytics_bp
from .chatbot import chatbot_bp
from .lead_generation import lead_generation_bp  # ✅ Import your blueprint
from .lead_qualification import lead_qualification_web_bp  # ✅ Import your blueprint



# Collect them for easy registration
all_blueprints = [
    core_bp,
    order_management_bp,
    credit_management_bp,
    payment_management_bp,
    order_fulfillment_bp,
    reports_bp,
    invoice_management_bp,
    dispute_resolution_bp,
    reporting_bp,
    cash_application_bp,
    analytics_bp,
    chatbot_bp,
    lead_generation_bp,
    lead_qualification_web_bp 
]
