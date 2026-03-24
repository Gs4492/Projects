import sqlite3
import os
from Infrastructure.Auth.Web.config import Config

def init_db(app):
    db_path = Config.DATABASE
    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role_id INTEGER,
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            ''')
            cursor.execute("INSERT INTO roles (name) VALUES ('Admin'), ('User')")
            conn.commit()
