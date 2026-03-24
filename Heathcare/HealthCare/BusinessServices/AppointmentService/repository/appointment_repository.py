# repository/appointment_repository.py

from utils.db import get_db_connection
from models.appointment import Appointment

def create_appointment(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_name, doctor_name, date, time, status) VALUES (?, ?, ?, ?, ?)",
        (data['patient_name'], data['doctor_name'], data['date'], data['time'], data['status'])
    )
    conn.commit()
    appt_id = cursor.lastrowid
    conn.close()
    return appt_id

def get_all_appointments():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM appointments").fetchall()
    conn.close()
    return [Appointment(**dict(row)) for row in rows]

def get_appointment_by_id(appointment_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
    conn.close()
    return Appointment(**dict(row)) if row else None

def update_appointment(appointment_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET patient_name = ?, doctor_name = ?, date = ?, time = ?, status = ? WHERE id = ?",
        (data['patient_name'], data['doctor_name'], data['date'], data['time'], data['status'], appointment_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_appointment(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_today_appointments(today_date):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM appointments WHERE date = ?", (today_date,)).fetchall()
    conn.close()
    return [Appointment(**dict(row)) for row in rows]
