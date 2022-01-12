import json
from pydantic import FilePath
import os
import shutil
from typing import Dict


def safe_json_write(obj: Dict, fp: FilePath):
    """
    Safely write files by first writing to a tmp file then copying to final location. This ensures that no file is
    partially written thus leaving a file in an unrecoverable place.

    Arguments:
        obj (Dict): The dictionary that should be written
        fp (FilePath): The path the file should be written at

    """

    tmp_fp = f"{fp}.tmp"

    if os.path.isfile(tmp_fp):
        os.remove(tmp_fp)

    try:
        with open(tmp_fp, "w") as fh:
            json.dump(obj, fh, indent=4)

    except Exception as e:
        raise e

    try:
        shutil.copyfile(tmp_fp, fp)
    except Exception as e:
        raise e

    os.remove(tmp_fp)