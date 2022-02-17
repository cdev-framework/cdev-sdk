# Generated as part of Resource Test project template
from cdev.resources.simple.xlambda import simple_function_annotation
from cdev.resources.simple.api import Api
from cdev.resources.simple.object_store import Bucket
from cdev.resources.simple.queue import Queue
from cdev.resources.simple.relational_db import RelationalDB, db_engine
from cdev.resources.simple.static_site import StaticSite
from cdev.resources.simple.table import Table, AttributeDefinition, KeyDefinition, attribute_type, key_type
from cdev.resources.simple.topic import Topic


# Api
myApi = Api("demoapi")
route1 = myApi.route('/hello', 'GET')

# Bucket
bucket = Bucket('demobucket')

# Queue
myQueue = Queue('bigqueue')


# Table
attributes = [AttributeDefinition('id', attribute_type.S)]
keys = [KeyDefinition('id', key_type.HASH)]

dinner_table = Table('dinner', attributes, keys)

# Topic
good_dinner_conversation_topic = Topic('of_discussion', nonce='1')


# Function
@simple_function_annotation("hello_world_function", permissions=[bucket.available_permissions.READ_AND_WRITE_BUCKET])
def hello_world(event, context):
    print('Hellow World!')