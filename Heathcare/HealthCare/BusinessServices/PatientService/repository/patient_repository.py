# repository/patient_repository.py

from utils.db import get_db_connection
from models.patient import Patient

def create_patient(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (name, age, gender, contact) VALUES (?, ?, ?, ?)",
        (data['name'], data['age'], data['gender'], data['contact'])
    )
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return patient_id

def get_all_patients():
    conn = get_db_connection()
    patients = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    return [Patient(**dict(row)) for row in patients]

def get_patient_by_id(patient_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conn.close()
    return Patient(**dict(row)) if row else None

def update_patient(patient_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE patients SET name = ?, age = ?, gender = ?, contact = ? WHERE id = ?",
        (data['name'], data['age'], data['gender'], data['contact'], patient_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
