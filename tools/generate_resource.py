from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import json

BOTO_BASE_PATH = "/home/daniel/cdev-org/botocore"

BOTO_DATA_PATH = os.path.join(BOTO_BASE_PATH, "botocore" ,"data")


env = Environment(
    loader=FileSystemLoader(os.path.join(".")),
    autoescape=select_autoescape()
)

with open(os.path.join(".","resources.json")) as fh:
    needed_resource_data = json.load(fh)

final_data = {}

for value in needed_resource_data.get("resources"):
    service_path = os.path.join(BOTO_DATA_PATH, value.get("service"), value.get("folder"), "service-2.json")
    
    with open(service_path) as fh:
        print(json.load(fh))

print(needed_resource_data)

template = env.get_template("resource-template.py.jinja")

print(template.render(**needed_resource_data))