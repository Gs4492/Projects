# repository/doctor_repository.py

from utils.db import get_db_connection
from models.doctor import Doctor

def create_doctor(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO doctors (name, specialty, contact, available) VALUES (?, ?, ?, ?)",
        (data['name'], data['specialty'], data['contact'], int(data.get('available', 1)))
    )
    conn.commit()
    doctor_id = cursor.lastrowid
    conn.close()
    return doctor_id

def get_all_doctors():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return [Doctor(**dict(row)) for row in rows]

def get_doctor_by_id(doctor_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
    conn.close()
    return Doctor(**dict(row)) if row else None

def update_doctor(doctor_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE doctors SET name = ?, specialty = ?, contact = ?, available = ? WHERE id = ?",
        (data['name'], data['specialty'], data['contact'], int(data['available']), doctor_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_available_doctors():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM doctors WHERE available = 1").fetchall()
    conn.close()
    return [Doctor(**dict(row)) for row in rows]
