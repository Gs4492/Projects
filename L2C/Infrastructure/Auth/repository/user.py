import sqlite3
from Infrastructure.Auth.Web.config import Config

def get_all_users():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user(user_id, username, password):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def find_user_by_username(username):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, password, role_id FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def register_user(username, password):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    # Assuming new users get role_id = 2 (User)
    cursor.execute('''
        INSERT INTO users (username, password, role_id) VALUES (?, ?, 2)
    ''', (username, password))
    conn.commit()
    conn.close()


def get_role_by_user_id(user_id):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT roles.name FROM roles
        JOIN users ON users.role_id = roles.id
        WHERE users.id = ?
    ''', (user_id,))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None

def update_user_permissions(username, permission):
    from Infrastructure.Auth.Web.config import Config
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False
    cursor.execute("UPDATE users SET permissions = ? WHERE username = ?", (permission, username))
    conn.commit()
    conn.close()
    return True


def assign_role_to_user(username, role_name):
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return False

    cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    role = cursor.fetchone()
    if not role:
        cursor.execute("INSERT INTO roles (name) VALUES (?)", (role_name,))
        conn.commit()
        role_id = cursor.lastrowid
    else:
        role_id = role[0]

    cursor.execute("UPDATE users SET role_id = ? WHERE username = ?", (role_id, username))
    conn.commit()
    conn.close()
    return True


