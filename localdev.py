import os
from importlib import reload
import src.parser.cdev_parser as cparser
import src
reload(src.parser.parser_objects); reload(src.parser.parser_utils); reload(cparser)

file_path = os.path.join(".", "tests", "sample_test.py")
