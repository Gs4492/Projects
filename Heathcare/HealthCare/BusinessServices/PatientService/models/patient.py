# models/patient.py

class Patient:
    def __init__(self, id, name, age, gender, contact):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.contact = contact

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact': self.contact
        }
