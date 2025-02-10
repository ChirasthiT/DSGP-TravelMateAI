class Location:
    def __init__(self, name, description, image_url):
        self.name = name
        self.description = description
        self.image_url = image_url

    @staticmethod
    def from_dict(data):
        return Location(data['name'], data['description'], data['image_url'])

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url
        }