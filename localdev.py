import os
from importlib import reload
import src.cdev.parser.cdev_parser as cparser
import src.cdev
reload(src.cdev.parser.cdev_parser_exceptions); reload(src.cdev.parser.parser_objects); reload(src.cdev.parser.parser_utils); reload(cparser)

file_path = os.path.join(".",  "localdev.py")

TEST_PATH = os.path.join(".","tests","example_files", "advanced")
