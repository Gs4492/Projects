class Invoice:
    def __init__(self, id, order_id, amount, payment_status, payment_date):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.payment_status = payment_status
        self.payment_date = payment_date

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date
        }
