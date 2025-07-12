class QualifiedLead:
    def __init__(self, id, name, email, score, qualified, created_at):
        self.id = id
        self.name = name
        self.email = email
        self.score = score
        self.qualified = qualified
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'score': self.score,
            'qualified': self.qualified,
            'created_at': self.created_at
        }
