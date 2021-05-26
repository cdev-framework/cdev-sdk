import os




def write_to_intermediate_function(fp, filename, lines):
    # Function takes a filepath (fp), filename, and lines then writes the lines to the file
    # This function is used to create the intermediate file
    # It creates the file on the file system and also returns metadata about the file

    if not os.path.isdir(fp):
        return None

    fullpath = os.path.join(fp,filename)

    with open(fullpath, "w") as fh:
        for line in lines:
            fh.write(line)

    return True


def write_intermediate_files(original_path, file_info):
    # Function takes an original file path and a file_info obj that describes what lines need to be parsed 
    # from the original file

    # file_info: dict<str, [(lineno,lineno)]>
    
    
    if not os.path.isfile(original_path):
        return None



    