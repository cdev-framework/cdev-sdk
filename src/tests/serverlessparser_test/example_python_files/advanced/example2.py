import os, importlib
import sys as sss
from datetime import date

today = date.today()

sss.path.append(os.path.join(".", "libs"))

# include <PPP>
for i in range(0, 5):
    # IMAGINE THIS DOES SOMETHING
    print(i)


def log(message):
    print(f"{today}: {message}")


def handler1(event, scope):
    log(message)
    print(sss.path)
