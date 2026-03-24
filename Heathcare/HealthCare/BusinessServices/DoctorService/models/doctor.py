# models/doctor.py

class Doctor:
    def __init__(self, id, name, specialty, contact, available):
        self.id = id
        self.name = name
        self.specialty = specialty
        self.contact = contact
        self.available = available  # 1 for available, 0 for not

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'contact': self.contact,
            'available': bool(self.available)
        }
