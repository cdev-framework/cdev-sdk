import os

def get_lines_from_file_list(file_list, function_info):
    # Get the list of lines from a file based on the function info provided
    line_nos = _compress_lines(function_info)

    actual_lines = []

    for i in line_nos:
        if i <= len(file_list):
            actual_lines.append(file_list[i-1])

    return actual_lines


def get_file_as_list(path):
    # Returns the file as a list of lines
    if not os.path.isfile:
        return None

    with open(path) as fh:
        rv = fh.read().splitlines()

    return rv


def _compress_lines(original_lines):
    # Takes input SORTED([(l1,l2), (l3,l4), ...])
    # returns [l1,...,l2,l3,...,l4]
    rv = []

    for pair in original_lines:
        for i in range(pair[0], pair[1]+1):
            if rv and rv[-1] == i:
                # if the last element already equals the current value continue... helps eleminate touching boundaries
                continue

            rv.append(i)

    return rv 