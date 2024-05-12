verbose = False
verboseN = 0
crew_env = "/home/jw/src/crewai/lib/.env"
counter = 1
memory = False
server = "OLLAMA"

from_date = "2023-05-11"
to_date = "2024-05-11"


def set_project_name(pname):
    with open(".projectname", "r") as f:
        pn = f.readline()
    newpn = int(pn) + 1
    f = open(".projectname", "w")
    f.write(f"{newpn}")
    f.close()
    return f"{pname}_{pn}"


# def trace(func):
#     @functools.wraps(func)
#       def wrapper(*args, **kwargs):
#         print(Fore.WHITE+Back.RED)
#         print('Calling {}'.format(func.__name__))
#         traceback.print_stack()
#         print(Fore.RESET+Back.RESET)
#         return func(*args, **kwargs)
#       return wrapper