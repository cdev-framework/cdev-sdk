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
=================MERGE SUCCEEDED===================

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
