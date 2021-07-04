from cdev.frontend.constructs import Cdev_Resource
from cdev.frontend.models import Rendered_Resource

class DynamoDBTable(Cdev_Resource):
    def __init__(self,name) -> None:
        super().__init__()
        self.name = name

    def render(self):
        return Rendered_Resource(**{
            "ruuid": "cdev:aws:dynamodb",
            "name": self.name,
            "hash": 1
        })
        