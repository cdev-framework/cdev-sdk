_warning_emoji = ":warning:"

_navigation_information = """
To navigate this utility, you can use the following keys:

[italic cyan]up-arrow[/italic cyan]: Return to the previous page
[italic cyan]down-arrow[/italic cyan]: Go to the next page
[italic cyan]e[/italic cyan]: Expand the content of the page using your terminals pager
[italic cyan]q[/italic cyan]: Quit the utility. You will be presented with a warning page before actually quitting the utility.

[italic cyan]left/right arrow[/italic cyan]: Select option on a page.
"""


INTRODUCTION_PAGE_TITLE = """CDEV ENVIRONMENT MERGER UTILITY"""


INTRODUCTION_PAGE_CONTENT = f"""
Welcome to the Cdev Project Merger Utility!

This utility is designed to help Cdev users safely merge their Cdev Environments during a git merge. The following pages will help guide through the process of selecting how you want merge your Cdev environments.

-----

The following pages can be broken down into two types:

[italic cyan]Addition Pages[/italic cyan]: This page will be displayed for each new Cdev environment on your git branch. You will be able to select wether you want to add the environment into the final merged environment.


[italic cyan]Update Pages[/italic cyan]: This page is displayed when the configuration of an Environment is different between the two branches. You will be presented with the two differing Environment configurations, and you will need to select which of the Environment configurations you want to keep.

-----
{_navigation_information}

"""

QUIT_PAGE_TITLE = """QUIT PAGE"""


QUIT_PAGE_CONTENT = f"""
[reverse yellow] {_warning_emoji*3} WARNING: READ BELOW INFO BEFORE PROCEEDING  {_warning_emoji*3} [/reverse yellow]

------

[italic red]You are attempting to quit the Cdev Merger Utility[/italic red]

If you choose to quit the utility before finishing and confirming your changes, you will have to manually merge your .cdev/cdev_project.json file.

------

To quit press -> [red]q[/red]
To return to the utility press -> [blue]up-arrow, down-arrow, left-arrow, right-arrow, e, enter[/blue]

"""


QUIT_PAGE_NAVBAR = """[bold red]q[/bold red]: QUIT; [bold blue]up-arrow[/bold blue]: RETURN; [bold blue]down-arrow[/bold blue]: RETURN; [bold blue]right-arrow[/bold blue]: RETURN; [bold blue]left-arrow[/bold blue]: RETURN; [bold blue]enter[/bold blue]: RETURN; [bold blue]e[/bold blue]: RETURN"""
