class Plant:
    def __init__(self, id, name, category, price, stock, image_url):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.image_url = image_url

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'image_url': self.image_url
        }
