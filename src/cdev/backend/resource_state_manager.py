from pathlib import PosixPath
import time
from typing import List, Tuple

from cdev.utils import hasher

from . import utils as backend_utils
from . import initializer as backend_initializer


from ..models import Rendered_Component, Rendered_State, Rendered_Resource, Resource_State_Difference, Component_State_Difference, Action_Type



def create_project_diffs(new_project_state: Rendered_State) -> List[Component_State_Difference]:
    """
    This function takes in a rendered component object creates a list[State_Difference] based on the difference between that and 
    the previous state.
    """
    rv = []

    previous_local_state = backend_utils.load_resource_state()

    if not previous_local_state:
        # Create COMPONENT and ALL RESOURCES
        for component in new_project_state.rendered_components:
            rv.append( Component_State_Difference(
                    **{
                        "action_type": Action_Type.CREATE,
                        "previous_component": None,
                        "new_component": component,
                        "resource_diffs": _create_resource_diffs(component.rendered_resources,[])
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
                        "resource_diffs": _create_resource_diffs(component.rendered_resources,[])
                    }
                )
            )

        elif component.hash in previous_hash_to_component and component.name in previous_name_to_component:
            # Even though the hash has remained same we need to check for name changes in the resources

            resource_diffs = _create_resource_diffs(component.rendered_resources, previous_name_to_component.get(component.name).rendered_resources)
            
            if len(resource_diffs)  == 0:
                print(f"KEEP SAME {previous_hash_to_component.get(component.hash).name}")
            else:
                print(f"UPDATE RESOURCE NAME {previous_hash_to_component.get(component.hash).name}")
                rv.append(
                    Component_State_Difference(
                        **{
                            "action_type": Action_Type.UPDATE_IDENTITY,
                            "previous_component": previous_hash_to_component.get(component.hash),
                            "new_component": component,
                            "resource_diffs": resource_diffs
                        }
                    )
                )


            continue

        if component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
            print(f"UPDATE NAME FROM {previous_hash_to_component.get(component.hash).name} -> {component.name} ")
            rv.append(
                Component_State_Difference(
                    **{
                        "action_type": Action_Type.UPDATE_NAME,
                        "previous_component": previous_hash_to_component.get(component.hash),
                        "new_component": component,
                        "resource_diffs": None
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
                        "resource_diffs": _create_resource_diffs(component.rendered_resources, previous_name_to_component.get(component.name).rendered_resources)
                    }
                )
            )



        # POP the seen previous component as we go so only remaining resources will be deletes
        
        # For each remaining resource:
            # DELETE object

        # append to rv

    return rv


def _create_resource_diffs(new_resources: List[Rendered_Resource], old_resource: List[Rendered_Resource]) -> List[Resource_State_Difference]:


    if old_resource:
        # build map<hash,resource>
        old_hash_to_resource = {x.hash: x for x in old_resource}
        # build map<name,resource>
        old_name_to_resource = {x.name: x for x in old_resource}
    else:
        old_hash_to_resource = {}
        old_name_to_resource = {}

    rv = []
    for resource in new_resources:
        if resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            #print(f"    KEEP SAME {old_hash_to_resource.get(resource.hash).name}")
            # POP the seen previous resources as we go so only remaining resources will be deletess
            old_resource.remove(old_hash_to_resource.get(resource.hash))
            continue
            
        elif resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            #print(f"    UPDATE NAME FROM {old_hash_to_resource.get(resource.hash).name} -> {resource.name}")
            rv.append(Resource_State_Difference(
                **{
                    "action_type": Action_Type.UPDATE_NAME,
                    "previous_resource": old_hash_to_resource.get(resource.hash),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))

        elif not resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            #print(f"    UPDATE IDENTITY FROM {old_name_to_resource.get(resource.name).hash} -> {resource.hash}")
            rv.append(Resource_State_Difference(
                **{
                    "action_type": Action_Type.UPDATE_IDENTITY,
                    "previous_resource": old_name_to_resource.get(resource.name),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_name_to_resource.get(resource.name))

        elif not resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            #print(f"CREATE {resource}")
            rv.append(Resource_State_Difference(
                **{
                    "action_type": Action_Type.CREATE,
                    "previous_resource": None,
                    "new_resource": resource
                }
            ))

    print(old_resource)
    for resource in old_resource:
        #print(f"DELETE {resource}")
        rv.append(Resource_State_Difference(
                **{
                    "action_type": Action_Type.DELETE,
                    "previous_resource": resource,
                    "new_resource": None
                }
            )
        )

    return rv


def handle_component_difference(diff: Component_State_Difference):
    """
    This function handles changes at the component level. Since a component is reflective of the resources that it contains,
    only light Creates and Update Name changes are handled at this level. This has to do with the fact that a component hash
    is defineded rendered resources, and at that stage of calling this function, the mappers have not deployed the resources,
    so we do not know if the resources have been created. 

    Create: Create an empty component with just the name. It will be populated by the mappers once the actual resources have been 
    created.

    Update Name: Do a quick change of the name of the component
    """
    
    if not backend_initializer.is_backend_initialized():
        print("BAD NO BACKEND")
        return None

    current_backend = backend_utils.load_resource_state()

    if diff.action_type == Action_Type.CREATE:
        if current_backend.rendered_components:
            current_backend.rendered_components.append(_create_skeleton_component(diff.new_component))
        else: 
            current_backend.rendered_components = [_create_skeleton_component(diff.new_component)]

    if diff.action_type == Action_Type.UPDATE_NAME:
        for rendered_component in current_backend.rendered_components:
            if rendered_component.hash == diff.new_component.hash:
                rendered_component.name = diff.new_component.name
                break

    backend_utils.write_resource_state(current_backend)


def _create_skeleton_component(rendered_component: Rendered_Component) -> Rendered_Component:
    return Rendered_Component(
        **{
            "rendered_resources": None,
            "hash": "",
            "name": rendered_component.name
        }
    )


def write_resource_difference(component_name: str, diff: Resource_State_Difference) -> bool:
    """
    This function handles changes at the resource level that have already occured. This happens downstream of the mapper deploying
    the resource, so we know that making the changes makes the rendered state more accurate to the deployed state. Because the basics
    of the component state have been handled upstream (basic creates and name changes) we can get the component by name.

    AFTER the change has been made we will need to recompute the component and project hashes. 

    Create: Append the resource to the component
    Update Identity: Overwrite the previous resource
    Update Name: Change the name of the resource
    Delete: Delete old resource
    """
    
    if not backend_initializer.is_backend_initialized():
        print("BAD NO BACKEND")
        return None

    current_backend = backend_utils.load_resource_state()
    
    for indx, rendered_component  in enumerate(current_backend.rendered_components):
        if rendered_component.name == component_name:
            previous_component = current_backend.rendered_components.pop(indx)
            
            
            if diff.action_type == Action_Type.CREATE:
                # Append the updated resource
                if previous_component.rendered_resources:
                    previous_component.rendered_resources.append(diff.new_resource)
                else:
                    previous_component.rendered_resources = [diff.new_resource]

            elif diff.action_type == Action_Type.UPDATE_IDENTITY:
                # Replace the previous components rendered resources with a list excluding the previous resource we are updating by hash
                previous_component.rendered_resources = [x for x in previous_component.rendered_resources if not x.hash == diff.previous_resource.hash]
                
                # Append the updated resource
                previous_component.rendered_resources.append(diff.new_resource)

            elif diff.action_type == Action_Type.UPDATE_NAME:
                # Replace the previous components rendered resources with a list excluding the previous resource we are updating by name
                previous_component.rendered_resources = [x for x in previous_component.rendered_resources if not x.name == diff.previous_resource.name]
                # Append the updated resource
                previous_component.rendered_resources.append(diff.new_resource)

            elif diff.action_type == Action_Type.DELETE:
                # Replace the previous components rendered resources with a list excluding the previous resource we are updating by hash
                previous_component.rendered_resources = [x for x in previous_component.rendered_resources if not x.hash == diff.previous_resource.hash]

            previous_component.rendered_resources.sort(key=lambda x: x.hash)
            previous_component.hash = hasher.hash_list([x.hash for x in previous_component.rendered_resources])

            current_backend.rendered_components.append(previous_component)
            break

    
    current_backend.rendered_components.sort(key=lambda x: x.name)
    current_backend.hash = hasher.hash_list([x.hash for x in current_backend.rendered_components])

    backend_utils.write_resource_state(current_backend)
        
