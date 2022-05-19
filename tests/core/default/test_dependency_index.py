""" from cdev.default.fs_manager import external_dependencies_index
from cdev.default.fs_manager.utils import ModulePackagingInfo, PackageTypes


fake_sizes = {
    "a": 10,
    "b": 5,
    "c": 10,
    "d": 20,
    "e": 12,
    "z": 50,
    "x": 20,
}

def modified_get_module_size(starting_path: str) -> int:
    return fake_sizes.get(starting_path)

external_dependencies_index.get_module_size = modified_get_module_size

##### Simple Test

mod_z = ModulePackagingInfo(**{
    "module_name": "Z",
    "type": PackageTypes.PIP,
    "version_id": "1.0.0",
    "fp": "z",
    "flat": []
})

mod_x = ModulePackagingInfo(**{
    "module_name": "X",
    "type": PackageTypes.PIP,
    "version_id": "2.0.0",
    "fp": "x",
    "flat": []
})


mod_a = ModulePackagingInfo(**{
    "module_name": "A",
    "type": PackageTypes.PIP,
    "version_id": "1.0.1",
    "fp": "a",
    "tree": [mod_z],
    "flat": [mod_z]
})


mod_b = ModulePackagingInfo(**{
    "module_name": "B",
    "type": PackageTypes.PIP,
    "version_id": "1.0.2",
    "fp": "b",
    "tree": [mod_z],
    "flat": [mod_z]
})


mod_c = ModulePackagingInfo(**{
    "module_name": "C",
    "type": PackageTypes.PIP,
    "version_id": "3.0.2",
    "fp": "c",
    "tree": [mod_x],
    "flat": [mod_x]
})


simple_test_input = [
    mod_a,
    mod_b,
    mod_c
]


simple_graph = external_dependencies_index.weighted_dependency_graph(simple_test_input)

simple_graph.print_graph()

index = external_dependencies_index.compute_index(simple_graph, 2)

print(index)

print(f"----------------------")

##### COMPLEX TEST

mod_e_complex = ModulePackagingInfo(**{
    "module_name": "E",
    "type": PackageTypes.PIP,
    "version_id": "1.0.0",
    "fp": "e",
    "tree": []
})

mod_d_complex = ModulePackagingInfo(**{
    "module_name": "D",
    "type": PackageTypes.PIP,
    "version_id": "1.0.1",
    "fp": "d",
    "tree": [mod_e_complex],
    "flat": [mod_e_complex]
})

mod_z_complex = ModulePackagingInfo(**{
    "module_name": "Z",
    "type": PackageTypes.PIP,
    "version_id": "1.0.0",
    "fp": "z",
})

mod_x_complex = ModulePackagingInfo(**{
    "module_name": "X",
    "type": PackageTypes.PIP,
    "version_id": "2.0.0",
    "fp": "x",
    "tree": [mod_e_complex, mod_d_complex],
    "flat": [mod_e_complex, mod_d_complex]
})


mod_a_complex = ModulePackagingInfo(**{
    "module_name": "A",
    "type": PackageTypes.PIP,
    "version_id": "1.0.1",
    "fp": "a",
    "tree": [mod_z_complex],
    "flat": [mod_z_complex]
})


mod_b_complex = ModulePackagingInfo(**{
    "module_name": "B",
    "type": PackageTypes.PIP,
    "version_id": "1.0.2",
    "fp": "b",
    "tree": [mod_z_complex, mod_d_complex],
    "flat": [mod_z_complex, mod_e_complex, mod_d_complex]
})


mod_c_complex = ModulePackagingInfo(**{
    "module_name": "C",
    "type": PackageTypes.PIP,
    "version_id": "3.0.2",
    "fp": "c",
    "tree": [mod_x_complex, mod_d_complex],
    "flat": [mod_x_complex, mod_e_complex, mod_d_complex]
})


complex_test_input = [
    mod_a_complex,
    mod_b_complex,
    mod_c_complex,
    mod_d_complex
]


complex_graph = external_dependencies_index.weighted_dependency_graph(complex_test_input)

complex_graph.print_graph()

complex_index = external_dependencies_index.compute_index(complex_graph, 2)

print(complex_index)

print(f"----------------------") """
