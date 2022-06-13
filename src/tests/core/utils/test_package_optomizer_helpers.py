from core.utils.fs_manager import package_optimizer


def test_find_all_top_modules():
    test_used_modules = set(["pandas", "six", "a", "f"])

    test_data = {
        "pandas": ["six"],
        "a": ["b", "c"],
        "b": [],
        "c": ["d"],
        "d": ["e"],
        "f": [],
    }

    rv = set(["pandas", "a", "f"])

    assert rv == package_optimizer._find_all_top_modules(test_used_modules, test_data)
