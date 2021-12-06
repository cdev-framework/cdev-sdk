from typing import Dict, List

from cdev.core.constructs import Resource_State, Cloud_Output



class Environment(Resource_State):
    _parent: 'Project' = None
    _children = None




class Project(Resource_State):

    _children: List[Environment] = []

    #################
    ##### Environment
    #################

    def get_environment(self) -> str:
        #return cdev_environment.get_current_environment()
        pass

    def add_output(self, label: str, output: Cloud_Output) -> None:
        # Output labels to display after a deployment
        self._outputs[label] = output


    def get_outputs(self) -> Dict:
        return self._outputs

