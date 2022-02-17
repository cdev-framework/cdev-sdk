from core.constructs.commands import BaseCommandContainer


class SimpleCommandContainer(BaseCommandContainer):
    help = """
These are the commands that are available for use on simple buckets.

cp: Copy files between your local workspace and a deployed bucket
sync: Sync the contents of a given folder to a deployed bucket

"""
