import os

SETTINGS = {
    
}

SETTINGS["BASE_PATH"] = os.path.abspath(os.getcwd())
SETTINGS["INTERNAL_FOLDER_NAME"] = os.path.join(SETTINGS.get("BASE_PATH"), ".cdev")

SETTINGS["CDEV_INTERMEDIATE_FOLDER_LOCATION"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "intermediate")
SETTINGS["CDEV_INTERMEDIATE_FILES_LOCATION"] = os.path.join(SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "functions")

SETTINGS["STATE_FOLDER"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "state")
SETTINGS["LOCAL_STATE_LOCATION"] = os.path.join(SETTINGS.get("STATE_FOLDER"), "localstate.json")

SETTINGS["CDEV_PROJECT_FILE"] = os.path.join(SETTINGS.get("BASE_PATH"), "cdev_project.py")
SETTINGS["COMPONENT_FILE_NAME"] = "cdev_component.py"
