import time
from typing import List, Tuple

from . import utils as backend_utils
from .models import Resource_State_Difference, Component_State_Difference, Action_Type

from cdev.frontend.models import Rendered_Component, Rendered_State, Rendered_Resource



def create_project_diffs(new_project: Rendered_State) -> List[Component_State_Difference]:
    """
    This function takes in a rendered component object creates a list[State_Difference] based on the difference between that and 
    the previous state.
    """

    previous_local_state = backend_utils.load_local_state()
    rv = []
    if not previous_local_state:
        # Create COMPONENT and ALL RESOURCES
        for component in new_project.rendered_components:
            rv.append( Component_State_Difference(
                    **{
                        "action_type": Action_Type.CREATE,
                        "previous_component": None,
                        "new_component": component,
                        "resource_diff": _create_resource_diffs(component.rendered_resources,[])
                    }
                )
            )

    # For each component in the new state
        # if there is same hash and same name
            # DO NOTHING

        # if there is the diff name and same hash
            # UPDATE NAME

        # if there is the same name and diff hash
            # UPDATE IDENTITY
            # _create_resource_diffs(new,old)

        # if there is diff hash and diff name 
            # Create COMPONENT and ALL RESOURCES
            # _create_resource_diffs(new,{})


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
            if not old_hash_to_resource.get(resource.hash) == old_name_to_resource.get(resource.name):
                print("BAD")
                # TODO throw err
            continue
            
        if resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            print(f"UPDATE NAME FROM {old_hash_to_resource.get(resource.hash).name} -> {resource.name}")

        if not resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            print(f"UPDATE IDENTITY FROM {old_name_to_resource.get(resource.name).hash} -> {resource.hash}")

        if not resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
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