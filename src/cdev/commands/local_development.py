import os
import sys
from time import sleep
from typing import List

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.live import Live
from rich.text import Text

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler



import logging
import threading
import time

from cdev import output as cdev_output

STD_OUT_HISTORY_BUFFER = []
history = []
Program_Executing = True



def make_develop_layout() -> Layout:
    layout = Layout("tmp")
    layout.split(
        
        Layout(name="stdout"),
        Layout(name="output"), 
        Layout(name="commands"), 
     
    )

    layout['stdout'].ratio = 70
    layout['output'].ratio = 20
    layout['commands'].ratio = 1
    #layout['hidden'].visible = False

    layout['commands'].update("[blink]----- Command ------[blink]")

    return layout



LAYOUT = make_develop_layout()
LIVE_OBJECT = Live(LAYOUT, auto_refresh=False, transient=True)

def develop(args):
    run_enhanced_local_development_environment(args)


def run_enhanced_local_development_environment(args):
    patterns = ["./src/*"]
    ignore_patterns = ["*/__pycache__/*"]
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    path = os.getcwd()
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    

    x = threading.Thread(target=handle_stdin, daemon=True)
    try:
        with LIVE_OBJECT as l:
            my_observer.start()
            x.start()
            last_stdout_hash = 0
            while True:
                messages, messages_hash = cdev_output.get_messages_from_buffer(None,None)
                
                

                if messages_hash == last_stdout_hash:
                    pass
                else:
                    print(messages)
                    messages_as_string = "\n".join(messages)
                    last_stdout_hash = messages_hash
                    LAYOUT['stdout'].update(Panel(messages_as_string))
                    update_screen()
                    sleep(.1)


    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
        x.join()
        print("Development environment closed")
        exit(0)


def handle_stdin():
    while Program_Executing:
        _new_line = []
        for line in sys.stdin.readline():
            _new_line.append(line)

        add_line_to_history("".join(_new_line))
        
        potential_new_line = get_new_lines()
        if potential_new_line:
            LAYOUT["output"].update(Panel(potential_new_line))
        
        update_screen()
            


def update_screen():
    LIVE_OBJECT.update(LAYOUT, refresh=True)


def add_line_to_history(line):
    history.append(line)

    

def get_new_lines() -> str:
    if not history:
        return None
    lines = '\n> '.join(history)
    rv = "> " + lines
    history.clear()
    return rv

from . import deploy, plan
def on_created(event):
    cdev_output.print(f"hey, [red]{event.src_path}[/red] has been created!")
    plan({})
    cdev_output.print(f"hey, [red]{event.src_path}[/red] has been created!")

def on_deleted(event):
    cdev_output.print(f"what the f**k! Someone deleted {event.src_path}!")
    #plan({})

def on_modified(event):
    cdev_output.print(f"hey buddy, {event.src_path} has been modified")
    #plan({})

def on_moved(event):
    cdev_output.print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
    #plan({})
