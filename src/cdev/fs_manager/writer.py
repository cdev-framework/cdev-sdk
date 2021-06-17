import os

from cdev.settings import SETTINGS as cdev_settings
from . import utils as fs_utils


BASE_FILES_PATH = cdev_settings.get("CDEV_INTERMEDIATE_FILES_LOCATION")



def write_intermediate_file(original_path, function_info, prefix=None):
    # Function takes an original file path and a file_info obj that describes what lines need to be parsed 
    # from the original file

    # Prefix is a variable that will be added to the path after the BASE PATH but before the split path

    # original_path: path to file
    # function_info: [{"function_name", "needed_lines"}]

    if not os.path.isfile(original_path):
        print(f"nah {original_path}")
        return None


    split_path = original_path.split("/")
    # the last item in the path is .py file name... change the  .py to _py so it works as a dir
    split_path[-1] = split_path[-1].split(".")[0] + "_py"
    try:
        split_path.remove(".")
        split_path.remove("..")
    except Exception as e:
        pass

    if prefix:
        split_path.insert(0, prefix)

    final_file_dir = _create_path(BASE_FILES_PATH, split_path)

    file_list =  fs_utils.get_file_as_list(original_path)


    actual_lines = fs_utils.get_lines_from_file_list(file_list, function_info.get("needed_lines"))
    _write_intermediate_function(final_file_dir, function_info.get("function_name"), actual_lines)

    return os.path.join(final_file_dir,function_info.get("function_name")+".py")

def _write_intermediate_function(fp, filename, lines):
    # Function takes a filepath (fp), filename, and lines then writes the lines to the file
    # This function is used to create the intermediate file
    # It creates the file on the file system and also returns metadata about the file

    if not os.path.isdir(fp):
        return None

    fullpath = os.path.join(fp,filename) + ".py"

    with open(fullpath, "w") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")

    return True


def _create_path(startingpath, fullpath):
    # This functions takes a starting path and list of child dir and makes them all
    # Returns the final path

    # ex: _create_path(""./basedir", ["sub1", "sub2"])
    # creates: 
    #   - ./basedir/sub1/
    #   - ./basedir/sub1/sub2

    if not os.path.isdir(startingpath):
        return None

    intermediate_path = startingpath

    for p in fullpath:
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path
