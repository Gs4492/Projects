class Order:
    def __init__(self, order_number, customer_name, order_date, status):
        self.order_number = order_number
        self.customer_name = customer_name
        self.order_date = order_date
        self.status = status

    def to_dict(self):
        return {
            "order_number": self.order_number,
            "customer_name": self.customer_name,
            "order_date": self.order_date,
            "status": self.status
        }
