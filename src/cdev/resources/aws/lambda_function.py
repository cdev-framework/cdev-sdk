import inspect

def lambda_function(*args, **kwargs):
    if args:
        name = args[0]

    events = kwargs.get("events")

    middleware = kwargs.get("middleware")

    env_vars = kwargs.get("middleware")

    def wrap_create_function(func):

        def create_function(*args, **kwargs):
            
            if inspect.isfunction(func):
                for item in inspect.getmembers(func):
                    if item[0] == "__name__":
                        function_name=item[1]
            
            rv = {
                "lambda_name": name,
                "handler_name": function_name,
                "events": events,
                "middleware": middleware
            }

            return rv

        return create_function

    return wrap_create_function
