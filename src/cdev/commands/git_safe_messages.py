#############################################
##### Help Messages
#############################################

no_command_message = """
Need to either supply a command. Run with the -h flag for all available commands:

cdev git-safe -h
"""

failed_merge_message = """
+++++++++++++++MERGE FAILED+++++++++++++++++

Cdev safe-git was not able to automatically merge the commits. Above are the errors raised directly by git for the merge. You will need to manually fix the failed files and finish the merge, or you can abandon the merge:

<Manually fix file>
git add <files>
cdev git-safe merge --continue

or

cdev git-safe merge --abort

++++++++++++++++++++++++++++++++++++++++++++
"""


failed_abort_merge_message = """
+++++++++++++++ABORT MERGE FAILED+++++++++++++++++

Cdev safe-git was not able to abort the current merge. Above are the errors raised directly by git for the abort.

++++++++++++++++++++++++++++++++++++++++++++
"""


failed_fetch_message = """
+++++++++++++++FETCH FAILED+++++++++++++++++

Cdev safe-git was not able to fetch the provided repository to complete the pull. Above are the errors raised directly by git for the fetch.

++++++++++++++++++++++++++++++++++++++++++++
"""

success_merge_message = """
=================MERGE SUCCEEDED===================

Cdev safe-git was able to complete the merge!

===================================================

"""


success_pull_message = """
=================MERGE SUCCEEDED===================

Cdev safe-git was able to complete the pull!

===================================================

"""


success_merge_abort_message = """
=================ABORT SUCCEEDED===================

Cdev safe-git was able to abort the merge!

===================================================

"""

failed_commit_message = """
+++++++++++++++COMMIT FAILED+++++++++++++++++

Cdev safe-git was not able to commit your changes to complete your merge. Above are the errors raised directly by git for the commit.

Once you have fixed your issues, you can continue with the merge with:

cdev git-safe merge --continue

++++++++++++++++++++++++++++++++++++++++++++

"""


failed_to_load_other_message = """
+++++++++++++++ERROR+++++++++++++++++

Cdev was not able to properly load the cdev_project.json file from the other branch. You will need to manually check that the .cdev/cdev_project.json file in the other commit is in a valid state.

This error will cause a merge conflict on the .cdev/cdev_project.json file. It is HIGHLY recommend that you abort this merge and fix the issue on the other brach manually before merging.

cdev git-safe merge --abort

++++++++++++++++++++++++++++++++++++++++++++

"""

failed_to_load_current_message = """
+++++++++++++++ERROR+++++++++++++++++

Cdev was not able to properly load the cdev_project.json file from the this branch. You will need to manually check that the .cdev/cdev_project.json file on this branch is in a valid state.

This error will cause a merge conflict on the .cdev/cdev_project.json file. It is HIGHLY recommend that you abort this merge and fix the issue on this brach manually before merging.

cdev git-safe merge --abort

++++++++++++++++++++++++++++++++++++++++++++

"""


exited_merge_message = """
+++++++++++++++ERROR+++++++++++++++++

You exited the cdev merge utility before completing all the information needed to properly merge your cdev environments.

This error will cause a merge conflict on the .cdev/cdev_project.json file. It is HIGHLY recommend that you abort this merge and retry your merge.

cdev git-safe merge --abort

++++++++++++++++++++++++++++++++++++++++++++

"""
