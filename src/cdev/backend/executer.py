import os


from . import initializer as backend_initializer
from . import state_manager 


def create_diffs(rendered_frontend: object) -> None:

    if not backend_initializer.is_backend_initialized():
        # TODO throw error
        print("NO BACKEND")
        backend_initializer.initialize_backend("project")


    for comp in rendered_frontend.get("rendered_resources"):
        print(state_manager.update_component_state(comp, comp.get("name")))
        
    # Modify local system to reflect changes
    #for action_type in actions:
    #    if action_type == "updates":
    #        _handler_update_actions(actions.get(action_type))
    #    elif action_type == "appends":
    #        _handle_append_actions(actions.get(action_type))
    #    elif action_type == "deletes":
    #        _handle_delete_actions(actions.get(action_type))


def _handle_append_actions(actions):
    #print(f"appends: {actions}")
    for append_action in actions:
        if not append_action.get("dependencies_hash") == "0":
            print(f"ADD NEW DEP {append_action}")


def _handle_delete_actions(actions):
    #print(f"deletes: {actions}")
    for delete_action in actions:
        os.remove(delete_action.get("parsed_path"))


def _handler_update_actions(actions):
    #print(f"updates: {actions}")

    for update_action in actions:
        if 'SOURCE CODE' in update_action.get("action"):
            # SOURCE CODE UPDATE
            print("HELLO")


    return


