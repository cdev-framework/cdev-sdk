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
    print("WHHy")
    if args:
        name = args[0]
        print(name)

    events = kwargs.get("events")

    middleware = kwargs.get("middleware")

    env_vars = kwargs.get("middleware")

    def wrap_create_function(func):
        print("EEFWEFW")
        def create_function(*args, **kwargs):
            print("DWOPEIFWE")
            rv = {
                "name": name,
                "events": "yyyy",
                "middleware": middleware
            }

            return rv

        return create_function

    return wrap_create_function
