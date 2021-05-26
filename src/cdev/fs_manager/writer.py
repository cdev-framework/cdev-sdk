import os

from cdev.settings import SETTINGS as cdev_settings


BASE_FILES_PATH = cdev_settings.get("CDEV_INTERMEDIATE_FILES_LOCATION")




def write_intermediate_files(original_path, file_info):
    # Function takes an original file path and a file_info obj that describes what lines need to be parsed 
    # from the original file

    # file_info: dict<str, [(lineno,lineno)]>
    if not os.path.isfile(original_path):
        print(f"nah {original_path}")
        return None

    file_list = _get_file_as_list(original_path)

    split_path = original_path.split("/")
    # the last item in the path is .py file name... change the  .py to _py so it works as a dir
    split_path[-1] = split_path[-1].split(".")[0] + "_py"
    split_path.remove(".")
    split_path.remove("..")
    print(split_path)
    final_file_dir = _create_path(BASE_FILES_PATH, split_path)
    print(final_file_dir)
    for info in file_info:
        line_nos = _compress_lines(file_info.get(info))

        actual_lines = []

        for i in line_nos:
            if i <= len(file_list):
                actual_lines.append(file_list[i-1])

        _write_intermediate_function(final_file_dir, info, actual_lines)



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
    if not os.path.isdir(startingpath):
        print(f"whyyy {startingpath}")
        return None

    intermediate_path = startingpath

    for p in fullpath:
        print(p)
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path



def _get_file_as_list(path):
    # Returns the file as a list of lines
    if not os.path.isfile:
        return None

    with open(path) as fh:
        rv = fh.read().splitlines()

    return rv

def _compress_lines(original_lines):
    # Takes input SORTED([(l1,l2), (l3,l4), ...])
    # returns [l1,..,l2,l3,...,l4]
    rv = []

    for pair in original_lines:
        for i in range(pair[0], pair[1]+1):
            if rv and rv[-1] == i:
                # if the last element already equals the current value continue... helps eleminate touching boundaries
                continue

            rv.append(i)

    return rv 



    