# Generated as part of the resource test project template
from cdev.aws.lambda_function import ServerlessFunction
from cdev.aws.api import Api
from cdev.aws.s3 import Bucket
from cdev.aws.sqs import Queue
from cdev.aws.relational_db import RelationalDB, db_engine
from cdev.aws.frontend import Site
from cdev.aws.dynamodb import (
    Table,
    AttributeDefinition,
    KeyDefinition,
    attribute_type,
    key_type,
)
from cdev.resources.simple.topic import Topic


# Api
myApi = Api("demoapi")
route1 = myApi.route("/hello", "GET")

# Bucket
bucket = Bucket("demobucket")

# Queue
myQueue = Queue("bigqueue")


# Table
attributes = [AttributeDefinition("id", attribute_type.S)]
keys = [KeyDefinition("id", key_type.HASH)]

dinner_table = Table("dinner", attributes, keys)

# Topic
good_dinner_conversation_topic = Topic("of_discussion", nonce="1")

# Serverless Relational DB
myDB = RelationalDB(
    cdev_name="demo_db",
    engine=db_engine.aurora_postgresql,
    username="username",
    password="password",
    database_name="default_table",
)

# Function
@ServerlessFunction(
    "hello_world_function",
    permissions=[bucket.available_permissions.READ_AND_WRITE_BUCKET],
)
def hello_world(event, context):
    print("Hellow World!")
