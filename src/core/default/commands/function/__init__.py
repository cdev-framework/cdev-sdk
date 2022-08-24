from core.constructs.commands import BaseCommandContainer


class SimpleCommandContainer(BaseCommandContainer):
    help = """
These are the commands that are available for use on the simple xlambda.

execute: Trigger a deployed function with a given event and context
logs: Get the logs from a deployed function
"""
