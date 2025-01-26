class Product:
    def __init__(self, product_id, name, category, price, description):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.description = description

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "description": self.description
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Product object from a dictionary.
        """
        return Product(
            product_id=data["product_id"],
            name=data["name"],
            category=data["category"],
            price=data["price"],
            description=data["description"]
        )

    def display_info(self):
        return f"Product ID: {self.product_id}\n" \
               f"Name: {self.name}\n" \
               f"Category: {self.category}\n" \
               f"Price: ${self.price:.2f}\n" \
               f"Description: {self.description}"

