import os
import sys
from time import sleep
from typing import Dict, List, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.live import Live
from rich.text import Text

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from cdev.utils import hasher

import threading
    
from ..utils import project
from ..frontend import executer as frontend_executer
from ..backend import executer as backend_executer
from ..backend import resource_state_manager, cloud_mapper_manager
    
from cdev import output as cdev_output
from cdev.settings import set_setting

from . import deploy

STD_OUT_HISTORY_BUFFER = []
history = []
Program_Executing = True

CLOUD_OUTPUT_BUFFER = "CLOUD_OUTPUT"

CURRENT_CONTEXT = {
    "is_deploy_running": False
}


def make_develop_layout() -> Layout:
    layout = Layout("tmp")
    layout.split(
        
        Layout(name="stdout"),
        Layout(name="cloud_output"), 
        Layout(name="commands"), 
     
    )

    layout['stdout'].ratio = 80
    layout['cloud_output'].ratio = 20
    layout['commands'].ratio = 1
    #layout['hidden'].visible = False

    layout['commands'].update("[blink]----- Command ------[blink]")
    layout['cloud_output'].update(Panel("", title="Cloud Output"))
    return layout



LAYOUT = make_develop_layout()
LIVE_OBJECT = Live(LAYOUT, auto_refresh=False, transient=True)

def develop(args):
    #set_setting("CAPTURE_OUTPUT", True)
    run_enhanced_local_development_environment(args)


def run_enhanced_local_development_environment(args):
    patterns = ["./src/*"]
    ignore_patterns = ["*/__pycache__/*"]
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = file_change_handler
    my_event_handler.on_deleted = file_change_handler
    my_event_handler.on_modified = file_change_handler
    my_event_handler.on_moved = file_change_handler

    path = os.getcwd()
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    

    handle_std_in_thread = threading.Thread(target=handle_std_input, daemon=True)
    cdev_output.create_buffer(CLOUD_OUTPUT_BUFFER)
    refresh_local_output({"buffer_name": CLOUD_OUTPUT_BUFFER, "reinitialize_project": True})
    my_observer.start()
    cdev_output.print(f"")
    cdev_output.print(f"[blink] *** waiting for changes ***[/blink]")
    
    try:
        while True:
            pass
        #with LIVE_OBJECT as l:
        #    refresh_output()
        #    handle_std_in_thread.start()
        #    last_stdout_hash = 0
        #    while True:
        #        messages, start_line_no, messages_hash = cdev_output.get_messages_from_buffer(-25,None)
        #        
        #        modified_messages = [f"({start_line_no+i}) {x}" for i,x in enumerate(messages,0)]
#
        #        if messages_hash == last_stdout_hash:
        #            pass
        #        else:
        #            
        #            messages_as_string = "\n".join(modified_messages)
        #            last_stdout_hash = messages_hash
        #            LAYOUT['stdout'].update(Panel(messages_as_string, title="STD OUT"))
        #            update_screen()
        #            
        #            sleep(.1)


    except KeyboardInterrupt:
        print("Development environment closed1")
        my_observer.stop()
        my_observer.join()
        handle_std_in_thread.join()
        exit(0)


def refresh_output():
    cdev_output.clear_buffer(CLOUD_OUTPUT_BUFFER)
    #refresh_local_output({"buffer_name": CLOUD_OUTPUT_BUFFER, "reinitialize_project": False})
    refresh_local_output({"reinitialize_project": False})
    #cloud_outputs,_,_ = cdev_output.get_messages_from_buffer(0,10, CLOUD_OUTPUT_BUFFER)
    #LAYOUT['cloud_output'].update(Panel("\n".join(cloud_outputs), title="Cloud Output"))



def handle_std_input():
    
    while True:
        command = []
        for line in sys.stdin.readline():
            # run command
            command.append(line)

        cdev_output.print("".join(command)[:-1])
        refresh_output()
        update_screen()


def file_change_handler(args):
    cdev_output.print(f"File Change Detected. Starting Deploy Process")
    deploy.local_deploy_command({})
    cdev_output.print(f"[blink] *** waiting for changes ***[/blink]")
    refresh_output()
    update_screen()




def update_screen():
    LIVE_OBJECT.update(LAYOUT, refresh=True)


def add_line_to_history(line):
    history.append(line)

    

def get_output_buffer() -> Tuple[str, str]:
    if not history:
        return None

    lines = '\n'.join(history)
    hash_val = hasher.hash_string(lines)

    #history.clear()
    return lines, hash_val


def local_development_deploy(args):

    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    
    if not backend_executer.validate_diffs(project_diffs):
        raise Exception 

    if not project_diffs:
        print("No differences to deploy")
        return

    backend_executer.deploy_diffs(project_diffs)
    refresh_local_output({})

    return 


def refresh_local_output(args: Dict):  

    if not "buffer_name" in args:
        write_to_buffer = False
    else:
        write_to_buffer = True

    if args.get("reinitialize_project"):
        project.initialize_project()
        frontend_executer.execute_frontend()


    PROJECT = project.Cdev_Project()
    
    desired_outputs = PROJECT.get_outputs()

    rendered_outputs = []

    for label, output in desired_outputs.items(): 
        
        identifier = output.resource.split("::")[-1]

        if output.transformer:
            rendered_value = cloud_mapper_manager.get_output_value(identifier, output.key, transformer=output.get("transformer"))
        else:
            rendered_value = cloud_mapper_manager.get_output_value(identifier, output.key)

        rendered_outputs.append(f"[magenta]{label}[/magenta] -> [green]{rendered_value}[/green]")

    
    for rendered_output in rendered_outputs:
        if not write_to_buffer:
            cdev_output.print(rendered_output)
        else:
            cdev_output.add_message_to_buffer(args.get("buffer_name"), str(rendered_output))

    


