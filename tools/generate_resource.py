from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import json
import pprint
import re

pp = pprint.PrettyPrinter()

BOTO_BASE_PATH = "/home/daniel/cdev-org/botocore"

BOTO_DATA_PATH = os.path.join(BOTO_BASE_PATH, "botocore" ,"data")

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_snake(name):
  new_name = pattern.sub('_', name).lower()
  return new_name


def _find_all_dependent_shapes(shape_name, all_needed_shapes, botoinfo):
  
    if shape_name not in botoinfo.get("shapes"):
        #print("BAD 1")
        return None

    if shape_name in all_needed_shapes:
        #print("Bad2")
        return all_needed_shapes
    
    if "structure" == botoinfo.get("shapes").get(shape_name).get("type"):
        for member_name,val in botoinfo.get("shapes").get(shape_name).get("members").items():
            all_needed_shapes.update(_find_all_dependent_shapes(val.get("shape"), all_needed_shapes, botoinfo))

    elif "list" == botoinfo.get("shapes").get(shape_name).get("type"):
        val = botoinfo.get("shapes").get(shape_name).get("member")
        all_needed_shapes.update(_find_all_dependent_shapes(val.get("shape"), all_needed_shapes, botoinfo))

    all_needed_shapes[shape_name] = botoinfo.get("shapes").get(shape_name)

    return all_needed_shapes


def flatten_structure(name, structure, shape_info) -> dict:
    rv = {}
    rv["name"] = name 
    rv["required"] = structure.get("required")
    rv["attributes"] = {}



    for member_name in structure.get("members"):
        s_name = structure.get("members").get(member_name).get("shape")
        if name == 'ProvisionedThroughput':
            print(structure)
            print(s_name)
            print(shape_info.get(s_name))
        
        if not s_name in shape_info:
            print(f"{name}: BAD SNAME NAME {member_name}; {s_name}")
        

        if shape_info.get(s_name).get("type") == "structure":
            rv["attributes"][member_name] = {"type": "structure", "name": s_name}
        elif shape_info.get(s_name).get("type") == "list":
            rv["attributes"][member_name] = {"type": "list",  "val_type": shape_info.get(s_name).get("member").get("shape")}
        elif shape_info.get(s_name).get("type") == "string" and 'enum' in shape_info.get(s_name):
            rv["attributes"][member_name] = {"type": "enum"}
        #elif shape_info.get(s_name).get("type") == "long":
        #    rv["attributes"][member_name] = {"type": "long"}
        else:
            rv["attributes"][member_name] = shape_info.get(s_name)

    return rv

def flatten_list(name, list_obj) -> dict:
    rv = {}
    rv["name"] = name 
    rv["type"] = list_obj.get("member").get("shape")


env = Environment(
    loader=FileSystemLoader(os.path.join(".")),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)
env.globals['flatten_structure'] = flatten_structure

with open(os.path.join(".","resources.json")) as fh:
    needed_resource_data = json.load(fh)

final_data = {}

for value in needed_resource_data.get("resources"):
    service_path = os.path.join(BOTO_DATA_PATH, value.get("service"), value.get("folder"), "service-2.json")
    
    with open(service_path) as fh:
        botoinfo = json.load(fh)

    if value.get('service') == "dynamodb" :

        FUNCTION_KEYS = ["create", "remove", "update"]
        function_key_to_function = {}
        for key in FUNCTION_KEYS:
            function_info = value.get(key)
            if isinstance(function_info,str):
                function_key_to_function[key] = botoinfo.get("operations").get(function_info)
            elif isinstance(function_info, dict):
                function_key_to_function[key] = botoinfo.get("operations").get(function_info.get("action"))

        
        #print(f"{value.get('service')}: {function_key_to_function}")
        tmp_func_names = [{"funcname":camel_to_snake(function_key_to_function.get(key).get("name"))} for key in function_key_to_function]
    
        dynamo_db_info = _find_all_dependent_shapes("CreateTableInput", {}, botoinfo)





template = env.get_template("resource-template.py.jinja")


final_info = {
    "functions": tmp_func_names, 
    "var": dynamo_db_info
}

rendered_template = template.render(**final_info,)

with open(os.path.join(".","t"), "w") as fh:
    fh.write(rendered_template)



