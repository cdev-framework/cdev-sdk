from cdev.mapper.fs_manager import external_dependencies_index 
from cdev.mapper.fs_manager.utils import ModulePackagingInfo, PackageTypes

mod_z = ModulePackagingInfo(**{
    "module_name": "Z",
    "type": PackageTypes.PIP,
    "version_id": "1.0.0",
    "fp": "z",
})

mod_x = ModulePackagingInfo(**{
    "module_name": "X",
    "type": PackageTypes.PIP,
    "version_id": "2.0.0",
    "fp": "x",
})


mod_a = ModulePackagingInfo(**{
    "module_name": "A",
    "type": PackageTypes.PIP,
    "version_id": "1.0.1",
    "fp": "a",
    "tree": [mod_z]
})


mod_b = ModulePackagingInfo(**{
    "module_name": "B",
    "type": PackageTypes.PIP,
    "version_id": "1.0.2",
    "fp": "b",
    "tree": [mod_z]
})


mod_c = ModulePackagingInfo(**{
    "module_name": "C",
    "type": PackageTypes.PIP,
    "version_id": "3.0.2",
    "fp": "c",
    "tree": [mod_x]
})




test_input = [
    mod_a,
    mod_b,
    mod_c
]

fake_sizes = {
    "a": 10,
    "b": 5,
    "c": 10,
    "z": 50,
    "x": 20,
}

def modified_get_module_size(starting_path: str) -> int:
    return fake_sizes.get(starting_path)


external_dependencies_index.get_module_size = modified_get_module_size

graph = external_dependencies_index.weighted_dependency_graph(test_input)

graph.print_graph()


index = external_dependencies_index.compute_index(graph, 2)

print(index)