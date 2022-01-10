from typing import Dict, Tuple, List
from core.constructs.components import Component, Component_Change_Type, ComponentModel, Component_Difference

from core.constructs.resource import Resource_Difference, Resource_Reference_Change_Type, Resource_Reference_Difference, ResourceModel, Resource_Change_Type, ResourceReferenceModel


class simple_component(Component):
    def __init__(self, name: str):
        super().__init__(name)


    def render(self) -> ComponentModel:
        return ComponentModel(
            self.name,
            "111"
        )


def simple_resource_data():
    return [
        ResourceModel("cdev::resource::x", "1", "resource1"),
        ResourceModel("cdev::resource::x", "2", "resource2"),
        ResourceModel("cdev::resource::x", "3", "resource3"),
        ResourceModel("cdev::resource::x", "4", "resource4"),
        ResourceModel("cdev::resource::x", "5", "resource5")
    ]


def simple_create_resource_changes(component_name: str) -> List[Resource_Difference]:
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


def simple_create_references(parent_component_name: str, component_name: str) -> List[Resource_Reference_Difference]:
    simple_resources = simple_resource_data()

    return [
        Resource_Reference_Difference(
            Resource_Reference_Change_Type.CREATE,
            component_name,
            ResourceReferenceModel(
                parent_component_name,
                x.ruuid,
                x.name,
            )
        ) for x in simple_resources
    ]


def simple_delete_references(parent_component_name: str, component_name: str) -> List[Resource_Reference_Difference]:
    simple_resources = simple_resource_data()

    return [
        Resource_Reference_Difference(
            Resource_Reference_Change_Type.DELETE,
            component_name,
            ResourceReferenceModel(
                parent_component_name,
                x.ruuid,
                x.name,
            )
        ) for x in simple_resources
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


def simple_component_differences() -> Tuple[List[ComponentModel], List[ComponentModel]]:
    """
    Return two lists of components that can be used for testing the differencing engine of a backend. The first list is the new
    desired component state and the second list is the previous state of the components.
    """

    basic_resource_set = [
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource1",
                "hash": "1",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource2",
                "hash": "2",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource3",
                "hash": "3",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource4",
                "hash": "4",
            }
        ),
    ]


    new_component2_resources = [
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource1",
                "hash": "1",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource2",
                "hash": "22",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource44",
                "hash": "4",
            }
        ),
        ResourceModel(
            **{
                "ruuid": "cdev::resource",
                "name": "resource5",
                "hash": "5",
            }
        ),
    ]

    basic_reference_set = [
        ResourceReferenceModel(
            **{
                "component_name": "comp1",
                "ruuid": "cdev::resource",
                "name": "resource1",
            }
        ),
        ResourceReferenceModel(
            **{
                "component_name": "comp1",
                "ruuid": "cdev::resource",
                "name": "resource2",
            }
        ),
    ]

    new_component2_reference_set = [
        ResourceReferenceModel(
            **{
                "component_name": "comp1",
                "ruuid": "cdev::resource",
                "name": "resource1",
            }
        ),
        ResourceReferenceModel(
            **{
                "component_name": "comp1",
                "ruuid": "cdev::resource",
                "name": "resource3",
            }
        ),
    ]

    new_component2 = ComponentModel(
        **{
            "name": "comp2",
            "hash": "1234",
            "resources": new_component2_resources,
            "references": new_component2_reference_set
        }
    )

    new_component4 = ComponentModel(
        **{
            "name": "comp4",
            "hash": "123456",
            "resources": [],
            "references": [],
        }
    )


    previous_component1 = ComponentModel(
        **{
            "name": "comp1",
            "hash": "123",
            "resources": basic_resource_set,
            "references": [],
        }
    )


    previous_component2 = ComponentModel(
        **{
            "name": "comp2",
            "hash": "1234",
            "resources": basic_resource_set,
            "references": basic_reference_set,
        }
    )

    previous_component3 = ComponentModel(
        **{
            "name": "comp3",
            "hash": "12345",
            "resources": [],
            "references": [],
        }
    )


    previous_component5 = ComponentModel(
        **{
            "name": "comp5",
            "hash": "123456",
            "resources": [],
            "references": [],
        }
    )

    # Component Diffs:
        # Component1 -> Same (This component should be read from the state and added to the new components during the test)
        # Component2 -> Update Identity
        # Component3 -> Delete
        # Component4 -> Create
        # Component5 -> Update Name (This component should be read from the state and then modify its name)
    return [new_component2, new_component4], [previous_component1, previous_component2, previous_component3, previous_component5]


def simple_components() -> List[Component]:
    component1 = simple_component("component1")
    component2 = simple_component("component2")
    component3 = simple_component("component3")


    return [
        component1,
        component2,
        component3
    ]


def simple_commands() -> List[str]:
    return [
        "data_sync",
        "logs",
        "price"
    ]



def simple_differences_for_topo_sort() -> Tuple[List[Component_Difference], List[Resource_Reference_Difference], List[Resource_Difference]]:
    """
    Generate a simple set of data to test for the correct of the topological sort of a set changes to be deployed. 

    Returns:
        Tuple[List[Component_Difference], List[Resource_Reference_Difference], List[Resource_Difference]]: The generated Data
    """
    
    component_diffs = [
        Component_Difference(
            action_type=Component_Change_Type.UPDATE_IDENTITY,
            previous_name="comp1",
            new_name="comp1"
        ),
        Component_Difference(
            action_type=Component_Change_Type.UPDATE_NAME,
            previous_name="comp2",
            new_name="comp22"
        ),
        Component_Difference(
            action_type=Component_Change_Type.UPDATE_IDENTITY,
            previous_name="comp3",
            new_name="comp3"
        ),
    ]

    
    resource_diffs = [
        Resource_Difference(
            action_type=Resource_Change_Type.CREATE,
            component_name="comp1",
            previous_resource=None,
            new_resource=ResourceModel(
                ruuid="cdev::test::r1",
                hash="123",
                name="r11"
            )
        ),
        Resource_Difference(
            action_type=Resource_Change_Type.UPDATE_IDENTITY,
            component_name="comp1",
            previous_resource=ResourceModel(
                ruuid="cdev::test::r1",
                hash="1234",
                name="r2"
            ),
            new_resource=ResourceModel(
                ruuid="cdev::test::r1",
                hash="1235",
                name="r2"
            )
        )
    ]

    reference_diffs = [
        Resource_Reference_Difference(
            action_type=Resource_Reference_Change_Type.CREATE,
            originating_component_name='comp3',
            resource_reference=ResourceReferenceModel(
                component_name="comp1",
                ruuid='cdev::test::r1',
                name='r11',
                
            )
        )
    ]


    return component_diffs, resource_diffs, reference_diffs

