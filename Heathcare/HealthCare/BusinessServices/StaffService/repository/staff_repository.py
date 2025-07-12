# repository/staff_repository.py

from utils.db import get_db_connection
from models.staff import Staff

def create_staff(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO staff (name, role, contact, active) VALUES (?, ?, ?, ?)",
        (data['name'], data['role'], data['contact'], int(data.get('active', 1)))
    )
    conn.commit()
    staff_id = cursor.lastrowid
    conn.close()
    return staff_id

def get_all_staff():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM staff").fetchall()
    conn.close()
    return [Staff(**dict(row)) for row in rows]

def get_active_staff():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM staff WHERE active = 1").fetchall()
    conn.close()
    return [Staff(**dict(row)) for row in rows]

def update_staff(staff_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE staff SET name = ?, role = ?, contact = ?, active = ? WHERE id = ?",
        (data['name'], data['role'], data['contact'], int(data['active']), staff_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
