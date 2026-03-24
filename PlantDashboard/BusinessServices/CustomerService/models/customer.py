class Customer:
    def __init__(self, id, name, email, phone, address, preferences):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.preferences = preferences

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'preferences': self.preferences
        }
