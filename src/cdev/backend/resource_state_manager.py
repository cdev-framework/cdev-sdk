from pathlib import PosixPath
import time
from typing import List, Tuple

from . import utils as backend_utils
from . import initializer as backend_initializer


from ..models import Rendered_Component, Rendered_State, Rendered_Resource, Resource_State_Difference, Component_State_Difference, Action_Type



def create_project_diffs(new_project_state: Rendered_State) -> List[Component_State_Difference]:
    """
    This function takes in a rendered component object creates a list[State_Difference] based on the difference between that and 
    the previous state.
    """
    rv = []

    previous_local_state = backend_utils.load_local_state()

    if not previous_local_state:
        # Create COMPONENT and ALL RESOURCES
        for component in new_project_state.rendered_components:
            rv.append( Component_State_Difference(
                    **{
                        "action_type": Action_Type.CREATE,
                        "previous_component": None,
                        "new_component": component,
                        "resource_diff": _create_resource_diffs(component.rendered_resources,[])
                    }
                )
            )

    if previous_local_state.rendered_components:
        # build map<hash,resource>
        previous_hash_to_component = {x.hash: x for x in previous_local_state.rendered_components}
        # build map<name,resource>
        previous_name_to_component = {x.name: x for x in previous_local_state.rendered_components}
    else:
        previous_hash_to_component = {}
        previous_name_to_component = {}


    #print(previous_hash_to_resource)

    for component in new_project_state.rendered_components:
        
        if not component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
            # Create COMPONENT and ALL RESOURCES
        
            rv.append( Component_State_Difference(
                    **{
                        "action_type": Action_Type.CREATE,
                        "previous_component": None,
                        "new_component": component,
                        "resource_diff": _create_resource_diffs(component.rendered_resources,[])
                    }
                )
            )

        elif component.hash in previous_hash_to_component and component.name in previous_name_to_component:
            print(f"KEEP SAME {previous_hash_to_component.get(component.hash).name}")
            continue
            # DO NOTHING

        if component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
            print(f"UPDATE NAME FROM {previous_hash_to_component.get(component.hash).name} -> {component.name} ")
            rv.append(
                Component_State_Difference(
                    **{
                        "action_type": Action_Type.UPDATE_NAME,
                        "previous_component": previous_hash_to_component.get(component.hash),
                        "new_component": component,
                        "resource_diff": None
                    }
                )
            )
            # UPDATE NAME

        if not component.hash in previous_hash_to_component and component.name in previous_name_to_component:
            # UPDATE IDENTITY
            print(f"UPDATE IDENTITY FROM {previous_name_to_component.get(component.name).hash} -> {component.hash} ")
            
            rv.append(
                Component_State_Difference(
                    **{
                        "action_type": Action_Type.UPDATE_IDENTITY,
                        "previous_component": previous_hash_to_component.get(component.hash),
                        "new_component": component,
                        "resource_diff": _create_resource_diffs(component.rendered_resources, previous_name_to_component.get(component.name).rendered_resources)
                    }
                )
            )



        # POP the seen previous component as we go so only remaining resources will be deletes
        
        # For each remaining resource:
            # DELETE object

        # append to rv

    return rv


def _create_resource_diffs(new_resources: List[Rendered_Resource], old_resource: List[Rendered_Resource]) -> List[Resource_State_Difference]:
    # build map<hash,resource>
    old_hash_to_resource = {x.hash: x for x in old_resource}
    # build map<name,resource>
    old_name_to_resource = {x.name: x for x in old_resource}

    rv = []
    for resource in new_resources:
        if resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            print(f"    KEEP SAME {old_hash_to_resource.get(resource.hash).name}")
            continue
            
        elif resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            print(f"    UPDATE NAME FROM {old_hash_to_resource.get(resource.hash).name} -> {resource.name}")

        elif not resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            print(f"    UPDATE IDENTITY FROM {old_name_to_resource.get(resource.name).hash} -> {resource.hash}")

        elif not resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            #print(f"CREATE {resource}")
            rv.append(Resource_State_Difference(
                **{
                    "action_type": Action_Type.CREATE,
                    "previous_resource": None,
                    "new_resource": resource
                }
            ))

        # POP the seen previous resources as we go so only remaining resources will be deletes

    # For each remaining resource:
        # DELETE object

    return rv


def write_component_difference(diff: Component_State_Difference):
    if not backend_initializer.is_backend_initialized():
        print("BAD NO BACKEND")
        return None

    current_backend = backend_utils.load_local_state()

    if diff.action_type == Action_Type.CREATE:
        if current_backend.rendered_components:
            current_backend.rendered_components.append(diff.new_component)
        else: 
            current_backend.rendered_components = [diff.new_component]

    backend_utils.write_local_state(current_backend)

