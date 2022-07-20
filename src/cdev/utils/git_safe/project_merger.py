from enum import Enum
from typing import Any, List, Tuple


from cdev.constructs.environment import environment_info
from cdev.default.project import local_project_info

from cdev.utils.display_manager import (
    select_data,
    SelectionPageContainer,
    TwoItemSelectionPage,
    SingleItemSelectionPage,
    single_item_selection_data,
    two_item_selection_data,
    InformationPage,
    DidNotCompleteSelections,
)


from cdev.utils.git_safe.project_merger_info import (
    INTRODUCTION_PAGE_CONTENT,
    INTRODUCTION_PAGE_TITLE,
    QUIT_PAGE_CONTENT,
    QUIT_PAGE_NAVBAR,
    QUIT_PAGE_TITLE,
    ADDITION_ENVIRONMENT_TEMPLATE,
    UPDATE_ENVIRONMENT_TEMPLATE,
    FINAL_PAGE_COMPLETE_TEMPLATE,
    FINAL_PAGE_INCOMPLETE_TEMPLATE,
)


class ExitedMerge(Exception):
    pass


def merge_local_project_info(
    other_project: local_project_info,
    current_project: local_project_info,
    difference_helper: "DifferenceHelper",
) -> local_project_info:
    """Semantically diff the provided local project info objects

    Args:
        other_project (local_project_info): _description_
        current_project (local_project_info): _description_

    Returns:
        _type_: _description_
    """

    merged_local_project_info = local_project_info(
        **{
            "project_name": difference_helper.semantic_merge_value(
                "project_name", other_project.project_name, current_project.project_name
            ),
            "environment_infos": difference_helper.semantic_merge_environments(
                other_project.environment_infos, current_project.environment_infos
            ),
            "default_backend_configuration": difference_helper.semantic_merge_value(
                "default_backend_configuration",
                other_project.default_backend_configuration,
                current_project.default_backend_configuration,
            ),
            "current_environment_name": difference_helper.semantic_merge_value(
                "current_environment_name",
                other_project.current_environment_name,
                current_project.current_environment_name,
            ),
            "settings_directory": difference_helper.semantic_merge_value(
                "settings_directory",
                other_project.settings_directory,
                current_project.settings_directory,
            ),
            "initialization_module": difference_helper.semantic_merge_value(
                "initialization_module",
                other_project.initialization_module,
                current_project.initialization_module,
            ),
        }
    )

    return merged_local_project_info


def _diff_environments(
    other_events: List[environment_info], current_events: List[environment_info]
) -> Tuple[
    List[environment_info],
    List[environment_info],
    List[Tuple[environment_info, environment_info]],
]:
    """Generate the differences between two provided environments. The semantics of the differences are relative to the current
    events. Computes the: environment additions, environment removes, and environment updates. Environment uniqueness is defined
    by the workspace.resource_state_uuid field.

    Args:
        other_events (List[environment_info]): _description_
        current_events (List[environment_info]): _description_

    Returns:
        Tuple[List[environment_info], List[environment_info], List[Tuple[environment_info,environment_info]]]: _description_
    """

    original_rs_id_to_events = {
        x.workspace_info.resource_state_uuid: x for x in other_events
    }

    current_rs_id_to_events = {
        x.workspace_info.resource_state_uuid: x for x in current_events
    }

    # Resource States that have been added in the current environment
    rs_addition_keys = set(current_rs_id_to_events.keys()).difference(
        set(original_rs_id_to_events.keys())
    )
    rs_additions = [current_rs_id_to_events.get(x) for x in rs_addition_keys]

    # Resource States that have been added in the current environment
    rs_difference_keys = set(original_rs_id_to_events.keys()).difference(
        set(current_rs_id_to_events.keys())
    )
    rs_differences = [original_rs_id_to_events.get(x) for x in rs_difference_keys]

    rs_sames = set(current_rs_id_to_events.keys()).intersection(
        set(original_rs_id_to_events.keys())
    )

    rs_changes = {
        x: _diff_single_environment(
            original_rs_id_to_events.get(x), current_rs_id_to_events.get(x)
        )
        for x in rs_sames
    }

    rs_updates = [
        (original_rs_id_to_events.get(k), current_rs_id_to_events.get(k))
        for k, v in rs_changes.items()
        if not v
    ]

    return rs_additions, rs_differences, rs_updates


def _diff_single_environment(
    original_events: environment_info, current_events: environment_info
) -> bool:
    original_event_dict = original_events.dict()
    current_event_dict = current_events.dict()

    return original_event_dict == current_event_dict


class SemanticMergeEnvironmentVerbs(str, Enum):
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    NONE = "NONE"


class DifferenceHelper:
    def __init__(self) -> None:
        pass

    def semantic_merge_environments(
        self,
        additions: List[environment_info],
        deletes: List[environment_info],
        updates: List[Tuple[environment_info, environment_info]],
    ) -> List[environment_info]:
        raise NotImplementedError

    def semantic_merge_value(
        self, key: str, other_value: Any, current_value: Any
    ) -> Any:
        raise NotImplementedError


class RichDifferenceHelper:
    def __init__(self) -> None:
        pass

    def semantic_merge_environments(
        self,
        other_environments: List[environment_info],
        current_environments: List[environment_info],
    ) -> List[environment_info]:
        adds, deletes, updates = _diff_environments(
            other_environments, current_environments
        )
        container = SelectionPageContainer(
            QUIT_PAGE_TITLE, QUIT_PAGE_CONTENT, QUIT_PAGE_NAVBAR
        )

        container.add_page(
            InformationPage(INTRODUCTION_PAGE_TITLE, INTRODUCTION_PAGE_CONTENT)
        )

        [
            container.add_page(
                SingleItemSelectionPage(
                    ADDITION_ENVIRONMENT_TEMPLATE.format(environment_name=x.name),
                    single_item_selection_data(
                        content=x.dict(),
                        options=[
                            ("ADD", (SemanticMergeEnvironmentVerbs.ADD, x)),
                            ("DONT ADD", (SemanticMergeEnvironmentVerbs.NONE, None)),
                        ],
                    ),
                )
            )
            for x in adds
        ]

        for original_env_info, current_env_info in updates:
            container.add_page(
                TwoItemSelectionPage(
                    UPDATE_ENVIRONMENT_TEMPLATE.format(
                        environment_name=current_env_info.name
                    ),
                    two_item_selection_data(
                        left_data=select_data(
                            "OTHER BRANCH VERSION",
                            original_env_info.dict(),
                            (SemanticMergeEnvironmentVerbs.NONE, None),
                        ),
                        right_data=select_data(
                            "CURRENT BRANCH VERSION",
                            current_env_info.dict(),
                            (SemanticMergeEnvironmentVerbs.UPDATE, current_env_info),
                        ),
                    ),
                )
            )

        try:
            container.run_pages()
        except DidNotCompleteSelections:
            raise ExitedMerge

        final_environments = _process_actions(
            other_environments, container.get_results()
        )

        return final_environments

    def semantic_merge_value(
        self, key: str, other_value: Any, current_value: Any
    ) -> Any:
        return current_value


def _process_actions(
    base_environments: List[environment_info],
    actions: List[Tuple[SemanticMergeEnvironmentVerbs, environment_info]],
):
    _copy_base_environments = base_environments.copy()

    for action, data in actions:
        if action == SemanticMergeEnvironmentVerbs.NONE:
            continue

        elif action == SemanticMergeEnvironmentVerbs.ADD:
            _copy_base_environments.append(data)

        elif action == SemanticMergeEnvironmentVerbs.UPDATE:
            _copy_base_environments = [
                x
                for x in _copy_base_environments
                if x.workspace_info.resource_state_uuid
                != data.workspace_info.resource_state_uuid
            ]
            _copy_base_environments.append(data)

        elif action == SemanticMergeEnvironmentVerbs.DELETE:
            _copy_base_environments = [
                x
                for x in _copy_base_environments
                if x.workspace_info.resource_state_uuid
                != data.workspace_info.resource_state_uuid
            ]

    return _copy_base_environments
