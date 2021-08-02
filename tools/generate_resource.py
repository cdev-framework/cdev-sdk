from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import json
import pprint
import re
from sortedcontainers import SortedList
from sortedcontainers.sortedlist import SortedListWithKey

pp = pprint.PrettyPrinter()

BOTO_BASE_PATH = "/home/daniel/cdev-org/botocore"

BOTO_DATA_PATH = os.path.join(BOTO_BASE_PATH, "botocore" ,"data")

pattern = re.compile(r'(?<!^)(?=[A-Z])')

TO_PYTHON_TYPES = {
    "string": "str",
    "boolean": "bool"
}



def camel_to_snake(name):
  new_name = pattern.sub('_', name).lower()
  return new_name

def pythonify_symbol(s: str):
    return s.replace("-", "_")


def _find_all_dependent_shapes(shape_name, all_needed_shapes, botoinfo, include_this):
  
    if shape_name not in botoinfo.get("shapes"):
        print("BAD 1")
        return None

    if shape_name in all_needed_shapes:
        #print("Bad2")
        return all_needed_shapes
    
    if "structure" == botoinfo.get("shapes").get(shape_name).get("type"):
        for member_name,val in botoinfo.get("shapes").get(shape_name).get("members").items():
            all_needed_shapes.update(_find_all_dependent_shapes(val.get("shape"), all_needed_shapes, botoinfo, True))

    elif "list" == botoinfo.get("shapes").get(shape_name).get("type"):
        val = botoinfo.get("shapes").get(shape_name).get("member")
        all_needed_shapes.update(_find_all_dependent_shapes(val.get("shape"), all_needed_shapes, botoinfo, True))

    elif "map" == botoinfo.get("shapes").get(shape_name).get("type"):
        key_val = botoinfo.get("shapes").get(shape_name).get("key")
        all_needed_shapes.update(_find_all_dependent_shapes(key_val.get("shape"), all_needed_shapes, botoinfo, True))
        value_val = botoinfo.get("shapes").get(shape_name).get("value")
        all_needed_shapes.update(_find_all_dependent_shapes(value_val.get("shape"), all_needed_shapes, botoinfo, True))

    if include_this:
        #print(f'{shape_name} -> {botoinfo.get("shapes").get(shape_name)}')
        all_needed_shapes[shape_name] = botoinfo.get("shapes").get(shape_name)

    return all_needed_shapes


def flatten_structure(name, structure, shape_info) -> dict:
    rv = {}
    rv["name"] = name 
    rv["required"] = structure.get("required")
    rv["attributes"] = {}
    rv["documentation"] = structure.get("documentation")


    for member_name in structure.get("members"):
        s_name = structure.get("members").get(member_name).get("shape")
        
        if not s_name in shape_info:
            print(f"{name}: BAD SNAME NAME {member_name}; {s_name}")
        

        if shape_info.get(s_name).get("type") == "structure":
            rv["attributes"][member_name] = {"type": "structure", "name": s_name}
            rv["attributes"][member_name]['documentation'] = structure.get("members").get(member_name).get("documentation")
        elif shape_info.get(s_name).get("type") == "list":

            if shape_info.get(shape_info.get(s_name).get("member").get("shape")).get("type") == "structure":

                rv["attributes"][member_name] = {"type": "list",  "val_type": shape_info.get(s_name).get("member").get("shape")}
                rv["attributes"][member_name]['documentation'] = shape_info.get(shape_info.get(s_name).get("member").get("shape")).get("documentation")
            else:
                original_val = shape_info.get(shape_info.get(s_name).get("member").get("shape")).get("type")
                rv["attributes"][member_name] = {"type": "list",  "val_type": TO_PYTHON_TYPES.get(original_val)}
                rv["attributes"][member_name]['documentation'] = shape_info.get(shape_info.get(s_name).get("member").get("shape")).get("documentation")

        elif shape_info.get(s_name).get("type") == "map":
            #print(f"{member_name}:: {s_name}" )

            key_type = ""
            val_type = ""
            key_shape = shape_info.get(s_name).get("key").get("shape")
            val_shape = shape_info.get(s_name).get("value").get("shape")


            if shape_info.get(key_shape).get("type") == "structure":
                key_type = key_shape
            else:
                key_type = TO_PYTHON_TYPES.get(shape_info.get(key_shape).get("type"))

            if shape_info.get(val_shape).get("type") == "structure":
                val_type = val_shape
            else:
                val_type = TO_PYTHON_TYPES.get(shape_info.get(val_shape).get("type"))

            rv["attributes"][member_name] = {"type": "map",  "val_type": val_type, "key_type": key_type }
            rv["attributes"][member_name]['documentation'] = structure.get("members").get(member_name).get("documentation")

        elif shape_info.get(s_name).get("type") == "string" and 'enum' in shape_info.get(s_name):
            rv["attributes"][member_name] = {"type": "enum", "name": s_name}
            rv["attributes"][member_name]['documentation'] = structure.get("members").get(member_name).get("documentation")
        else:
            rv["attributes"][member_name] = shape_info.get(s_name)
            rv["attributes"][member_name]['documentation'] = structure.get("members").get(member_name).get("documentation")

    return rv


def flatten_list(name, list_obj) -> dict:
    rv = {}
    rv["name"] = name 
    rv["type"] = list_obj.get("member").get("shape")


def flatten_attributes_to_params(attributes: list):
    final_string = ""

    sorted_attributes = SortedListWithKey(attributes, lambda x: not x.get("isrequired"))


    for attribute in sorted_attributes:
        if attribute.get("type") == "structure":
            final_string = f"{final_string}, {attribute.get('param_name')}: {attribute.get('name')}{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "list":
            final_string = f"{final_string}, {attribute.get('param_name')}: List[{attribute.get('val_type')}]{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "string":
            final_string = f"{final_string}, {attribute.get('param_name')}: str{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "integer":
            final_string = f"{final_string}, {attribute.get('param_name')}: int{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "enum":
            final_string = f"{final_string}, {attribute.get('param_name')}: {attribute.get('name')}{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "boolean":
            final_string = f"{final_string}, {attribute.get('param_name')}: bool{'=None' if not attribute.get('isrequired') else ''}"
        if attribute.get("type") == "map":
            final_string = f"{final_string}, {attribute.get('param_name')}: Dict[{attribute.get('key_type')}, {attribute.get('val_type')}]{'=None' if not attribute.get('isrequired') else ''}"

    return final_string[2:]

def create_attributes_for_rendered_resource_from_create_info(info, botoinfo):
    actual_shape = botoinfo.get("shapes").get(info.get("input").get("shape"))
    
    flattened_info = flatten_structure(info.get("name"), actual_shape, botoinfo.get("shapes"))
    #print(flattened_info)
    final_attributes = []

    for k,v in flattened_info.get("attributes").items():
        tmp = dict(v)
        tmp["isrequired"] = k in flattened_info.get("required")
        tmp["param_name"] = k
        final_attributes.append(tmp)

    return final_attributes

def create_output_attributes_from_create_info(info, botoinfo):

    
    members = botoinfo.get("shapes").get(info.get("output").get("shape")).get("members")

    if len(members.keys())== 1:
        key = [k for k in members][0]
        actual_shape_name = members.get(key).get("shape")
    else:
        actual_shape_name = info.get("output").get("shape")


    #print(actual_shape_name)
    actual_shape =  botoinfo.get("shapes").get(actual_shape_name)
    final_attributes = []
     

    if actual_shape.get("type") == "structure":
        for k in actual_shape.get("members"):
            
            final_attributes.append({"label": k, "documentation": actual_shape.get("members").get(k).get("documentation")})
    elif actual_shape.get("type") == "string":
        final_attributes.append({"label": key, "documentation": "st"})
    else:
        print(f"UNSUPPORTED TYPE IN create_output_attributes_from_create_info: type {actual_shape.get('type')}")

    return final_attributes



env = Environment(
    loader=FileSystemLoader(os.path.join(".")),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)
env.globals['flatten_structure'] = flatten_structure
env.globals['pythonify_symbol'] = pythonify_symbol


with open(os.path.join(".","resources.json")) as fh:
    needed_resource_data = json.load(fh)



def render_resources():
    for service in needed_resource_data.get("services"):
        
        FUNCTION_KEYS = ["create", "remove", "update"]
        service_path = os.path.join(BOTO_DATA_PATH, service.get("service"), service.get("folder"), "service-2.json")

        with open(service_path) as fh:
            botoinfo = json.load(fh)

        shapes = {}
        all_resource_info = []
        output_models = []

        for value in service.get("resources"):

            function_key_to_function = {}
            
            for key in FUNCTION_KEYS:
                function_info = value.get(key)
                if not function_info:
                    print("HERE")
                    continue

                if isinstance(function_info,str):
                    function_value = botoinfo.get("operations").get(function_info)
                elif isinstance(function_info, dict):
                    function_value = botoinfo.get("operations").get(function_info.get("action"))

                function_key_to_function[key] = function_value
                #print(function_value)

                tmp_func_names = [{"funcname":camel_to_snake(function_key_to_function.get(key).get("name"))} for key in function_key_to_function]

                shapes.update(_find_all_dependent_shapes(function_value.get("input").get("shape"), {}, botoinfo, False))


                if key == "create":
                    # Create resource based on the Params for this function
                    resource_attributes = create_attributes_for_rendered_resource_from_create_info(function_value, botoinfo)
                    
                    output_attributes = create_output_attributes_from_create_info(function_value, botoinfo)
                    #print(output_attributes)
                    output_model_info = {"name": f'{value.get("name")}_output', "attributes": output_attributes, 'documentation': function_value.get('documentation') }
                    output_models.append(output_model_info)

                    resource_info = {"resource_name": f'{value.get("name")}_model', "attributes": resource_attributes, "as_params": flatten_attributes_to_params(resource_attributes), "documentation": function_value.get('documentation')}
                    all_resource_info.append(resource_info)
                    
                    

        
        final_info = {
            "var": shapes,
            "resources": all_resource_info,
            "service": value.get('service'),
            "output_models": output_models 
        }
    
        template1 = env.get_template("resource-model-template.py.jinja")
        rendered_template1 = template1.render(**final_info)
        with open(os.path.join(".","output",f"{service.get('service')}_models.py"), "w") as fh:
            fh.write(rendered_template1)
        



if __name__ == "__main__":
    # execute only if run as a script
    render_resources()
