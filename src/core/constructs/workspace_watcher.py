"""Construct that represents the collection of other primitives


"""
import time
from watchdog.tricks import Trick

from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager
from watchdog.observers import Observer


class WorkspaceWatcher(Trick):
    """Executes some commands in response to modified files."""

    _patterns_to_watch = ("*.py",)
    _patterns_to_ignore = ("*.html", "README.md")

    def __init__(self, workspace: Workspace, output: OutputManager):
        super().__init__(
            patterns=self._patterns_to_watch,
            ignore_patterns=self._patterns_to_ignore,
            ignore_directories=False,
        )
        self._workspace = workspace
        self._output = output

    def watch(self):
        base_folder = self._workspace.settings.BASE_PATH
        observer = Observer()
        observer.schedule(self, base_folder, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def on_any_event(self, event):

        if event.is_directory:
            object_type = "directory"
        else:
            object_type = "file"

        context = {
            "watch_src_path": event.src_path,
            "watch_dest_path": "",
            "watch_event_type": event.event_type,
            "watch_object": object_type,
        }

        if hasattr(event, "dest_path"):
            context.update({"watch_dest_path": event.dest_path})
            print(
                'echo "${watch_event_type} ${watch_object} from ${watch_src_path} to ${watch_dest_path}"'.format(**context)
            )
        else:
            print(
                'echo "${watch_event_type} ${watch_object} ${watch_src_path}"'.format(**context)
            )
