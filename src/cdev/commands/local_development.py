import os
import sys
from time import sleep
from typing import List

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from cdev import output as cdev_output

STD_OUT_BUFFER = []
print(STD_OUT_BUFFER)

def develop(args):
    run_enhanced_local_development_environment(args)


def run_enhanced_local_development_environment(args):
    cdev_output.start_capturing_console()
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
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


    full_layout = make_develop_layout()

    
    full_layout["stdout"].update(Panel("RIGHT NOW"))
    full_layout["hidden"].update("[blink]----- Command ------[blink]")

    history = []
    stdout_buffer = []
    
    try:
        with Live(full_layout, auto_refresh=False, transient=True) as l:
            my_observer.start()
            while True:
                
                line =  sys.stdin.readline()
                history.append(line)
                
                full_layout["output"].update(Panel("> "+str("\n> ".join(history[-2:]))))

                l.update(full_layout, refresh=True)
                
                
               

                new_string = "\n".join(get_buffer())
                reset_buffer()
                full_layout['stdout'].update(Panel("No NEW CONTENT"))
                l.update(full_layout, refresh=True)

                if not new_string:
                    full_layout['stdout'].update(Panel(str(new_string)))
                    l.update(full_layout, refresh=True)
                
                else:                   
                    full_layout['stdout'].update(Panel(new_string))
                    l.update(full_layout, refresh=True)


    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
        print("Development environment closed")
        exit(0)


def make_develop_layout() -> Layout:
    layout = Layout("tmp")
    layout.split(
        
        Layout(name="stdout"),
        Layout(name="output"), 
        Layout(name="hidden"), 
     
    )

    layout['stdout'].ratio = 70
    layout['output'].ratio = 20
    layout['hidden'].ratio = 1
    #layout['hidden'].visible = False

    return layout

def get_buffer() -> List:
    return STD_OUT_BUFFER

def reset_buffer():
    STD_OUT_BUFFER = []

def on_created(event):
    STD_OUT_BUFFER.append(f"hey, {event.src_path} has been created!")

def on_deleted(event):
    STD_OUT_BUFFER.append(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    STD_OUT_BUFFER.append(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    STD_OUT_BUFFER.append(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")