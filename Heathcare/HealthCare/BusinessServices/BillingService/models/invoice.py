# models/invoice.py

class Invoice:
    def __init__(self, id, patient_name, amount, status, date):
        self.id = id
        self.patient_name = patient_name
        self.amount = amount
        self.status = status
        self.date = date

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'amount': self.amount,
            'status': self.status,
            'date': self.date
        }
