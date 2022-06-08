import time
from typing import Optional

from watchdog.tricks import Trick

from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager
from core.commands.deploy_differences import execute_deployment
from watchdog.observers import Observer


class WorkspaceWatcher(Trick):
    """Executes some commands in response to modified files."""

    _default_patterns_to_watch = ["src/**/*.py", "settings/*"]
    _default_patterns_to_ignore = [".cdev/**", "__pycache__/*"]

    def __init__(
        self,
        workspace: Workspace,
        output: OutputManager,
        no_default: Optional[bool] = False,
        patterns_to_watch: Optional[str] = None,
        patterns_to_ignore: Optional[str] = None
    ) -> None:

        self._observer = None
        self._workspace = workspace
        self._output = output
        self._base_folder = self._workspace.settings.BASE_PATH
        self._perform_deployment = False

        all_patterns_to_watch = None
        all_patterns_to_ignore = None

        if patterns_to_watch:
            all_patterns_to_watch = patterns_to_watch.split(",")

        if not no_default:
            all_patterns_to_watch += self._default_patterns_to_watch

        if patterns_to_ignore:
            all_patterns_to_ignore = patterns_to_ignore.split(",")

        if not no_default:
            all_patterns_to_ignore += self._default_patterns_to_ignore

        super().__init__(
            patterns=all_patterns_to_watch,
            ignore_patterns=all_patterns_to_ignore,
            ignore_directories=False,
        )

    def watch(self) -> None:
        print("Watching for changes in the workspace...")
        # Prevent multiples observers
        self._stop()

        self._observer = Observer()
        self._observer.schedule(self, self._base_folder, recursive=True)
        self._observer.start()
        try:
            while True:
                if self._perform_deployment:
                    # print('Ignoring future changes until deployment is finished')
                    execute_deployment(self._workspace, self._output)
                    # print('Enabling watch again')
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
