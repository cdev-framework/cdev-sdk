import os
import shutil

base_dir = os.path.join(os.path.dirname(__file__), "tmp")


if not os.path.isdir(base_dir):
    os.mkdir(base_dir)


# Delete any files in the tmp directory before running the tests
for f in os.listdir(base_dir):
    item = os.path.join(base_dir, f)
    if os.path.isdir(item):
        shutil.rmtree(item)

    if os.path.isfile(item):
        os.remove(item)
