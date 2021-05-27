class Resource:
    def __init__(self):

        self.tags = {}
        self.last_edited = ""
        pass


class Serverless_Function(Resource):
    def __init__(self, original_location, src_code, handler_name, runtime):
        super().__init__()
        self.original_location = original_location
        self.src_code = src_code
        self.handler_name = handler_name
        self.runtime = runtime

        self.parsed_location = None


class LocalState:
    # Initialize it to a previous local state file 
    # Pass an non exsiting file for creating a new state
    def __init__(self, path_to_state):
        
        pass
