from typing import Dict, Tuple, List

from core.constructs.resource import Resource_Difference, ResourceModel, Resource_Change_Type


def simple_resource_data():
    return [
        ResourceModel("cdev::resource::x", "1", "resource1"),
        ResourceModel("cdev::resource::x", "2", "resource2"),
        ResourceModel("cdev::resource::x", "3", "resource3"),
        ResourceModel("cdev::resource::x", "4", "resource4"),
        ResourceModel("cdev::resource::x", "5", "resource5")
    ]



def simple_create_resource_changes(component_name: str):
    simple_resources = simple_resource_data()
    return [
        Resource_Difference(
            Resource_Change_Type.CREATE,
            component_name,
            previous_resource=None,
            new_resource=simple_resources[0]
        ),
        Resource_Difference(
            Resource_Change_Type.CREATE,
            component_name,
            previous_resource=None,
            new_resource=simple_resources[1]
        ),
        Resource_Difference(
            Resource_Change_Type.CREATE,
            component_name,
            previous_resource=None,
            new_resource=simple_resources[2]
        ),
        Resource_Difference(
            Resource_Change_Type.CREATE,
            component_name,
            previous_resource=None,
            new_resource=simple_resources[3]
        ),
        Resource_Difference(
            Resource_Change_Type.CREATE,
            component_name,
            previous_resource=None,
            new_resource=simple_resources[4]
        )
    ]


def simple_create_resource_change_with_output(component_name: str) -> List[Tuple[Resource_Difference, Dict]]:
    return [(x,{"arn": f"{x.new_resource.ruuid}::{x.new_resource.name}"}) for x in simple_create_resource_changes(component_name) ]

def simple_delete_resource_changes(component_name: str):
    simple_resources = simple_resource_data()
    return [
        Resource_Difference(
            Resource_Change_Type.DELETE,
            component_name,
            previous_resource=simple_resources[0],
            new_resource=None
        ),
        Resource_Difference(
            Resource_Change_Type.DELETE,
            component_name,
            previous_resource=simple_resources[1],
            new_resource=None
        ),
        Resource_Difference(
            Resource_Change_Type.DELETE,
            component_name,
            previous_resource=simple_resources[2],
            new_resource=None
        ),
        Resource_Difference(
            Resource_Change_Type.DELETE,
            component_name,
            previous_resource=simple_resources[3],
            new_resource=None
        ),
        Resource_Difference(
            Resource_Change_Type.DELETE,
            component_name,
            previous_resource=simple_resources[4],
            new_resource=None
        )
    ]