import time
from typing import Optional, Callable

from pydantic import FilePath
from watchdog.tricks import Trick

from core.constructs.output_manager import OutputManager
from watchdog.observers import Observer


class StaticSiteWatcher(Trick):
    """Executes some commands in response to modified files."""

    _default_patterns_to_watch = ["*.html", "*.js", "*.jpg", "*.png"]
    _default_patterns_to_ignore = [".cdev/**", "__pycache__/*", "*.py"]

    def __init__(
        self,
        base_folder: FilePath,
        deployment_function: Callable,
        no_prompt: Optional[bool] = False,
        no_default: Optional[bool] = False,
        patterns_to_watch: Optional[str] = None,
        patterns_to_ignore: Optional[str] = None,
        output: "Console" = None,
    ) -> None:

        self._base_folder = base_folder
        self._deployment_function = deployment_function
        self._no_prompt = no_prompt
        self._output = output
        self._observer = None
        self._perform_deployment = False

        all_patterns_to_watch = None
        if patterns_to_watch:
            all_patterns_to_watch = patterns_to_watch.split(",")

        if not no_default:
            if all_patterns_to_watch:
                all_patterns_to_watch += self._default_patterns_to_watch
            else:
                all_patterns_to_watch = self._default_patterns_to_watch

        all_patterns_to_ignore = None
        if patterns_to_ignore:
            all_patterns_to_ignore = patterns_to_ignore.split(",")

        if not no_default:
            if all_patterns_to_ignore:
                all_patterns_to_ignore += self._default_patterns_to_ignore
            else:
                all_patterns_to_ignore = self._default_patterns_to_ignore

        super().__init__(
            patterns=all_patterns_to_watch,
            ignore_patterns=all_patterns_to_ignore,
            ignore_directories=False,
        )

    def watch(self) -> None:
        self._output.write("Watching for changes in the static site...")
        # Prevent multiples observers
        self._stop()

        self._observer = Observer()
        self._observer.schedule(self, self._base_folder, recursive=True)
        self._observer.start()
        try:
            while True:
                if self._perform_deployment:
                    self._deploy_static_files()
                    self._perform_deployment = False
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self._stop()

    def on_any_event(self, event):
        self._perform_deployment = True

    def _stop(self) -> None:
        if not self._observer:
            return

        observer = self._observer
        self._observer = None
        observer.stop()
        observer.join()

    def _deploy_static_files(self):
        self._output.write("Ignoring future changes until deployment is finished")
        self._deployment_function()
        self._output.write("Enabling watch again")
