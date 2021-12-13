import networkx as nx
from typing import List, Tuple, Generator, Any, Dict

from ..constructs.resource import Resource_Change_Type, Resource_Difference, ResourceModel

from ..constructs.components import  Component_Change_Type, ComponentModel, Component_Difference
from ..utils import  logger

log = logger.get_cdev_logger(__name__)


def create_project_diffs(new_project_state: List[ComponentModel], previous_local_state: List[ComponentModel]) -> Tuple[List[Component_Difference], List[Resource_Difference]]:
    """
    This function takes in a rendered component object creates a list[State_Difference] based on the difference between that and 
    the previous state.
    """
    component_rv = []
    resource_rv = []

    # build map<hash,resource>
    previous_hash_to_component = {x.hash: x for x in previous_local_state}
    # build map<name,resource>
    previous_name_to_component = {x.name: x for x in previous_local_state}
    previous_components_to_remove = [x for x in previous_local_state]
    

    #log.debug(f"previous_hash_to_component -> {previous_hash_to_component}")
    #log.debug(f"previous_name_to_component -> {previous_name_to_component}")


    for component in new_project_state:
        if not component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
            # Create COMPONENT and ALL RESOURCES
            #log.info(f"CREATE COMPONENT -> {component.name}")
            component_rv.append( Component_Difference(
                    **{
                        "action_type": Component_Change_Type.CREATE,
                        "previous_name": None,
                        "new_name": component.name
                    }
                )
            )

            resource_diffs = _create_resource_diffs(component.uuid, component.rendered_resources, [])

        elif component.hash in previous_hash_to_component and component.name in previous_name_to_component:
            # Since the hash is the same we can infer all the resource hashes are the same
            # Even though the hash has remained same we need to check for name changes in the resources

            resource_diffs = _create_resource_diffs(
                                component.name, 
                                component.rendered_resources, 
                                previous_name_to_component.get(component.name).rendered_resources
                            )

            
            resource_rv.extend(resource_diffs)
            
            # POP the seen previous component as we go so only remaining resources will be deletes
            previous_components_to_remove.remove(previous_name_to_component.get(component.name))

        elif component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
            # hash of the component has stayed the same but the user has renamed the component name
            # log.info(f"UPDATE NAME FROM {previous_hash_to_component.get(component.hash).name} -> {component.name}")
            component_rv.append(
                Component_Difference(
                    **{
                        "action_type": Component_Change_Type.UPDATE_NAME,
                        "previous_name": previous_hash_to_component.get(component.name).name,
                        "new_name": component.name
                    }
                )
            )
            # POP the seen previous component as we go so only remaining resources will be deletes
            previous_components_to_remove.remove(previous_hash_to_component.get(component.hash))

        elif not component.hash in previous_hash_to_component and component.name in previous_name_to_component:
            # hash of the component has changed but not the name 
            # log.info(f"UPDATE IDENTITY FROM {previous_name_to_component.get(component.name).hash} -> {component.hash} ")
            _create_resource_diffs(
                component.name, 
                component.rendered_resources, 
                previous_name_to_component.get(component.name).rendered_resources
            )

            resource_rv.extend(resource_diffs)
            
            # POP the seen previous component as we go so only remaining resources will be deletes
            previous_components_to_remove.remove(previous_name_to_component.get(component.name))


    #log.debug(previous_components_to_remove)
    for removed_component in previous_components_to_remove:
        #print(removed_component)
        #log.debug(removed_component)
        component_rv.append( Component_Difference(
                **{
                    "action_type": Component_Change_Type.DELETE,
                    "previous_name": None,
                    "new_name": removed_component.name
                }
            )
        )


    return component_rv, resource_rv


def _create_resource_diffs(component_name: str, new_resources: List[ResourceModel], old_resource: List[ResourceModel]) -> List[Resource_Difference]:

    #log.debug(f"calling _create_resource_diff with args (new_resources:{new_resources}, old_resources:{old_resource}")
    if old_resource:
        # build map<hash,resource>
        old_hash_to_resource = {x.hash: x for x in old_resource}
        # build map<name,resource>
        old_name_to_resource = {x.name: x for x in old_resource}
    else:
        old_hash_to_resource = {}
        old_name_to_resource = {}

    #log.debug(f"old_hash_to_resource -> {old_hash_to_resource}")
    #log.debug(f"old_name_to_resource -> {old_name_to_resource}")

    rv = []
    for resource in new_resources:
        if resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            #log.info(f"same resource diff {old_hash_to_resource.get(resource.hash).name}")
            # POP the seen previous resources as we go so only remaining resources will be deletess
            old_resource.remove(old_hash_to_resource.get(resource.hash))
            continue
            
        elif resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            print(f"update resource diff {old_hash_to_resource.get(resource.hash)} name {old_hash_to_resource.get(resource.hash).name} -> {resource.name}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.UPDATE_NAME,
                    "component_uuid": component_name,
                    "previous_resource": old_hash_to_resource.get(resource.hash),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))

        elif not resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            #log.info(f"update resource diff {old_name_to_resource.get(resource.name)} hash {old_name_to_resource.get(resource.name).hash} -> {resource.hash}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.UPDATE_IDENTITY,
                    "component_uuid": component_name,
                    "previous_resource": old_name_to_resource.get(resource.name),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_name_to_resource.get(resource.name))

        elif not resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            #log.info(f"create resource diff {resource}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.CREATE,
                    "component_uuid": component_name,
                    "previous_resource": None,
                    "new_resource": resource
                }
            ))

    if old_resource:
        for resource in old_resource:
            #log.info(f"delete resource diff {resource}")
            rv.append(Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.DELETE,
                        "component_uuid": component_name,
                        "previous_resource": resource,
                        "new_resource": None
                    }
                )
            )

    return rv


def generate_sorted_resources(resource_diffs: List[Resource_Difference]) -> Generator[Resource_Difference, None, None]:
    # nx graphs work on the element level by using the __hash__ of objects added to the graph, and to avoid making every obj support __hash__
    # we are using the id of {x.component_uuid};{x.new_resource.ruuid};{x.new_resource.hash} to identify resources in the graph then use a dict to map back to 
    # the actual object
    resource_dag = nx.DiGraph()

    
    # build dict from {x.new_resource.ruuid}::{x.new_resource.hash} to resource
    new_resource_id_to_resource_diff = {f"{x.component_uuid};{x.new_resource.ruuid};{x.new_resource.hash}":x for x in resource_diffs if x.new_resource }
    

    # this is used as the first check in the translation from parent_references by name
    new_resource_name_to_resource_diff = {f"{x.component_uuid};{x.new_resource.ruuid};{x.new_resource.name}":x for x in resource_diffs if x.new_resource }


    # build previous dict from {x.new_resource.ruuid}::{x.new_resource.hash} to resource
    previous_resource_id_to_resource_diff = {f"{x.component_uuid};{x.previous_resource.ruuid};{x.previous_resource.hash}":x for x in resource_diffs if not x.new_resource }
    

    # this is used as the first check in the translation from parent_references by name
    previous_resource_name_to_resource_diff = {f"{x.component_uuid};{x.previous_resource.ruuid};{x.previous_resource.name}":x for x in resource_diffs if not x.new_resource }

    # We don't want to reference output of diffs that are deletes so do not include the previous diffs
    all_resource_id_to_resource_diff = {}
    all_resource_id_to_resource_diff.update(new_resource_id_to_resource_diff)
    all_resource_id_to_resource_diff.update(previous_resource_id_to_resource_diff)
    

    for resource_diff in resource_diffs:
        if resource_diff.new_resource:
            log.info(f"FINDING PARENTS FOR {resource_diff.new_resource.name}")
            log.info(f"PARENTS {resource_diff.new_resource.parent_resources}")
            resource_id = f"{resource_diff.new_resource.ruuid};{resource_diff.new_resource.hash}"
            if resource_diff.new_resource.parent_resources:
                # IF the above resource has parent resources then we need to render their output and make sure this deployment
                # happens after
                resource_dag.add_node(resource_id)

                # A resource can have a parent listed twice via a name and id so need to keep track of the parents we have add already to make sure we don't try to readd
                seen_parents = set()

                for parent_reference in resource_diff.new_resource.parent_resources:
                    # A parent reference can be either ruuid:hash:<hash> or ruuid:name:<name>
                    # if the parent is reference by name means we need to look up the current hash of that parent. 
                    parent_resource_split = parent_reference.split(";")

                    if parent_resource_split[1] == "name":
                        # do lookup by name to get hash
                        name_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"
                        if name_identifier in new_resource_name_to_resource_diff:
                            parent_resource = new_resource_name_to_resource_diff.get(name_identifier)

                        else:
                            # If the parent resource is not in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    
                    else:
                        hash_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"

                        if hash_identifier in new_resource_id_to_resource_diff:
                            parent_resource = new_resource_id_to_resource_diff.get(hash_identifier)
                        
                        else:
                            # If the parent resource is not in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    


                    parent_resource_id = f"{parent_resource.new_resource.ruuid};{parent_resource.new_resource.hash}"
                    
                    if parent_resource_id in seen_parents:
                        log.debug(f"Already seen parent {parent_resource_id} for {resource_diff.new_resource.name}; {seen_parents}")
                        continue

                    log.info(f"PARENT RESOURCE {parent_resource_id} for {resource_diff.new_resource.name}")
                    # IF the parent is in the diff make this resource a descandant in the DAG
                    resource_dag.add_node(parent_resource_id)
                    resource_dag.add_edge(parent_resource_id, resource_id)
                    seen_parents.add(parent_resource_id)
        
            else:
                # IF this resource has no parents then add it as a top level resource in the DAG
                resource_dag.add_node(resource_id)
        
        else:
            # IF no new resource then this is a delete then we need to find any parents that are also being delete. Since these are delete, we want to delete
            # parents after the resource so change the direction of the connection in the dag

            resource_id = f"{resource_diff.previous_resource.ruuid};{resource_diff.previous_resource.hash}"

            if resource_diff.previous_resource.parent_resources:
                # IF the above resource has parent resources then we need to render their output and make sure this deployment
                # happens after
                resource_dag.add_node(resource_id)

                # A resource can have a parent listed twice via a name and id so need to keep track of the parents we have add already to make sure we don't try to readd
                seen_parents = set()

                for parent_reference in resource_diff.previous_resource.parent_resources:                
                    # A parent reference can be either ruuid:hash:<hash> or ruuid:name:<name>
                    # if the parent is reference by name means we need to look up the current hash of that parent. 
                    parent_resource_split = parent_reference.split(";")

                    if parent_resource_split[1] == "name":
                        # do lookup by name to get hash
                        name_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"
                        if name_identifier in previous_resource_name_to_resource_diff:
                            parent_resource = previous_resource_name_to_resource_diff.get(name_identifier)

                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    
                    else:
                        hash_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"

                        if hash_identifier in previous_resource_id_to_resource_diff:
                            parent_resource = previous_resource_id_to_resource_diff.get(hash_identifier)
                        
                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    


                    parent_resource_id = f"{parent_resource.previous_resource.ruuid};{parent_resource.previous_resource.hash}"
                    
                    if parent_resource_id in seen_parents:
                        log.debug(f"Already seen parent {parent_resource_id} for {resource_diff.previous_resource.name}; {seen_parents}")
                        continue

                    log.info(f"PARENT RESOURCE {parent_resource_id} for {resource_diff.previous_resource.name}")
                    # IF the parent is in the diff make this resource a descandant in the DAG
                    resource_dag.add_node(parent_resource_id)
                    resource_dag.add_edge(resource_id, parent_resource_id)
                    seen_parents.add(parent_resource_id)
            else:
                resource_dag.add_node(resource_id)
                log.info(f"ADDING {resource_id} AS DELETE")


    resource_dag = nx.topological_sort(resource_dag)

    return (all_resource_id_to_resource_diff.get(x) for x in resource_dag)



