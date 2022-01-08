from typing import Dict, List
from core.constructs.resource import Cloud_Output


def find_cloud_output(obj: dict) -> List[Cloud_Output]:

    rv = _recursive_replace_output(obj)

    return rv


def _recursive_replace_output(obj) -> List:
    rv = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                if "type" in v and v.get("type") == "cdev_output":
                    rv.append(Cloud_Output(**v))
                else:
                    rv.extend(_recursive_replace_output(v))

            elif isinstance(v, list):
                all_items_rendered = [_recursive_replace_output(x) for x in v]

                for item in all_items_rendered:
                    rv.extend(item)

        return rv

    elif isinstance(obj, list):
        all_items_rendered = [_recursive_replace_output(x) for x in obj]

        for item in all_items_rendered:
            rv.extend(item)

    return rv
