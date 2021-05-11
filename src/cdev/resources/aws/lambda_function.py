import inspect


def stripDecarators(code):
    # Remove all decorators that are at the beginning of the function
    codelist = code.splitlines()
    newsrc = []
    finished = False
    while codelist:
        tmp = codelist.pop(0)

        if not tmp:
            newsrc.append(tmp)
            continue

        if tmp[0] == "@" and not finished:
            continue

        newsrc.append(tmp)
        finished = True

    return "\n".join(newsrc)


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
