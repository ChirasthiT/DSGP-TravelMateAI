class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def from_dict(data):
        return Location(data['name'], data['description'])

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,

        }