project_not_merged = """
+++++++++++++++RESOURCE STATE CLEANUP FAILED+++++++++++++++++

Cdev safe-git was not able to automatically check for the correct resource states because your .cdev/cdev_project.json file has merge conflict. This could be because you did not complete the information in Cdev merger utility.

To fix this issue, you can:

Abort the merge:
    cdev git-safe merge --abort

or

Manually fix the merge conflict in the .cdev/cdev_project.json and stage the file:
    <manually fix merge conflict>
    git add .cdev/cdev_project.json

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


project_file_edited = """
+++++++++++++++RESOURCE STATE CLEANUP FAILED+++++++++++++++++

Cdev safe-git was not able to automatically check for the correct resource states because your .cdev/cdev_project.json file has changes that have not been staged.

To fix this issue, you can:

Stage your changes:
    git add .cdev/cdev_project.json

or

Undo the changes in your working directory:
    git checkout -- .cdev/cdev_project.json

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


project_file_reading = """
+++++++++++++++RESOURCE STATE CLEANUP FAILED+++++++++++++++++

Cdev safe-git was not able to automatically check for the correct resource states because your .cdev/cdev_project.json file because the current version is not able to be properly read.

You should not continue with this merge:

cdev git-safe merge --abort

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


preserve_resource_states = """
+++++++++++++++RESOURCE STATE CLEANUP FAILED+++++++++++++++++

Cdev safe-git was not able to automatically preserve needed resource states by removing deleted files from the staged area. You will need to check the contents of your git staging area and .cdev/cdev_project.json file to find the issue.

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
