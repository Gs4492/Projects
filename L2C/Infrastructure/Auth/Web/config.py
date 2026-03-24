import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, '../dal/user_management.db')
    SECRET_KEY = 'super-secret-key-123'  # Use a secure key in prod

