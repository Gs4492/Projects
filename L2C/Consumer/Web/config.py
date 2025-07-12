
# Consumer/Web/app/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    # Add other config vars as needed
