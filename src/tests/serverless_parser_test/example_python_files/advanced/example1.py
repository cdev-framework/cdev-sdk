import os, importlib
import sys as sss

global x

h = os.path.join(".")
x = os.environ.get("lkwem")

x = "Hello"
y = x[0]

glob = 1


def f1():
    def u():
        print("wowow")

    return glob


def t_function():
    print(y)
    t = "Hi"
    assert f1() == 4
    print(sss)


def b():
    print(t_function())
