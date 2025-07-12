# models/appointment.py

class Appointment:
    def __init__(self, id, patient_name, doctor_name, date, time, status):
        self.id = id
        self.patient_name = patient_name
        self.doctor_name = doctor_name
        self.date = date
        self.time = time
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'doctor_name': self.doctor_name,
            'date': self.date,
            'time': self.time,
            'status': self.status
        }
