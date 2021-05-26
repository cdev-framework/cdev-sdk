import os

SETTINGS = {
    
}

SETTINGS["CDEV_INTERMEDIATE_FOLDER_LOCATION"] = os.path.join(os.getcwd() , ".cdev", "intermediate")
SETTINGS["CDEV_INTERMEDIATE_FILES_LOCATION"] = os.path.join(SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "functions")

