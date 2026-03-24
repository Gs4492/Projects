class Lead:
    def __init__(self, id, name, email, phone, source, status, created_at):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.source = source
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at
        }
