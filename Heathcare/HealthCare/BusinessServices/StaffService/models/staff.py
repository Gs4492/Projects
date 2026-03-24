# models/staff.py

class Staff:
    def __init__(self, id, name, role, contact, active):
        self.id = id
        self.name = name
        self.role = role
        self.contact = contact
        self.active = active  # 1 = active/on-duty, 0 = off-duty

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'contact': self.contact,
            'active': bool(self.active)
        }
