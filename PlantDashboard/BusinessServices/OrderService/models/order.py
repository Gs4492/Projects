class Order:
    def __init__(self, id, customer_name, plant_name, quantity, total_price, status):
        self.id = id
        self.customer_name = customer_name
        self.plant_name = plant_name
        self.quantity = quantity
        self.total_price = total_price
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'plant_name': self.plant_name,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status
        }
