from typing import Dict

from cdev.core.constructs.backend import Backend_Configuration, Backend


class Local_Backend_Configuration(Backend_Configuration):
    def __init__(self, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": "cdev.default.backend.Local_Backend", 
            "config": config
        })


class Local_Backend(Backend):
    pass