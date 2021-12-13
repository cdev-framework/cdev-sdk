import os

from cdev.default import backend

# Monkey patch the file location to be ./tmp
backend.DEFAULT_CENTRAL_STATE_FOLDER = os.path.join(os.path.dirname(__file__), "tmp")
backend.DEFAULT_CENTRAL_STATE_FILE = os.path.join(backend.DEFAULT_CENTRAL_STATE_FOLDER, "local_state.json")

# Delete any files in the tmp directory before running
for f in os.listdir(backend.DEFAULT_CENTRAL_STATE_FOLDER):
    os.remove(os.path.join(backend.DEFAULT_CENTRAL_STATE_FOLDER, f))



mybackend = backend.LocalBackend()


new_state_uuid = mybackend.create_resource_state("", "project_state")

print(new_state_uuid)


actual_state = mybackend.list_top_level_resource_states()

print(actual_state)

#mybackend.delete_resource_state(new_state_uuid)

#print(mybackend)

mybackend.create_component(new_state_uuid, "component1")
mybackend.create_component(new_state_uuid, "component1")

