from dataclasses import dataclass
from enum import Enum
import termios, sys, tty
from typing import Any, Dict, List, Tuple

from rich.layout import Layout
from rich.pretty import Pretty
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

from cdev.utils.git_safe.project_merger_info import (
    FINAL_PAGE_COMPLETE_TEMPLATE,
    FINAL_PAGE_INCOMPLETE_TEMPLATE,
)


class DidNotCompleteSelections(Exception):
    pass


class KEY_ACTIONS(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    EXPAND = "EXPAND"
    QUIT = "QUIT"
    ENTER = "ENTER"


DEFAULT_KEY_BINDINGS = {
    b"\x1b[A": KEY_ACTIONS.UP,
    b"\x1b[B": KEY_ACTIONS.DOWN,
    b"\x1b[C": KEY_ACTIONS.RIGHT,
    b"\x1b[D": KEY_ACTIONS.LEFT,
    b"e": KEY_ACTIONS.EXPAND,
    b"q": KEY_ACTIONS.QUIT,
    b"\x03": KEY_ACTIONS.QUIT,
    b"\r": KEY_ACTIONS.ENTER,
}


class PAGE_EXIT_CODES(str, Enum):
    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    ACTION = "ACTION"
    EXPAND = "EXPAND"
    QUIT = "QUIT"


class PAGE_NAV_EMOJIS(str, Enum):
    COMPLETE = ":heavy_check_mark:"
    INCOMPLETE = ":cross_mark:"
    INFORMATION = ":page_with_curl:"


@dataclass
class select_data:
    header: str
    content: Any
    rv: Any


@dataclass
class split_layout:
    base: Layout
    right: Layout
    left: Layout


@dataclass
class two_item_selection_data:
    left_data: select_data
    right_data: select_data


@dataclass
class single_item_selection_data:
    options: List[Tuple[str, Any]]
    content: Any


class Page:
    def __init__(self) -> None:
        self.base_layout = Layout()
        self.nav: Layout = None

    def blocking_selection_process(self) -> PAGE_EXIT_CODES:
        raise NotImplementedError

    def update_navigation_bar(self, nav_content: Panel) -> None:
        self.nav.update(nav_content)

    def expand_view(self) -> None:
        raise NotImplementedError


class InformationPage(Page):
    def __init__(self, header: str, content: Any) -> None:
        super().__init__()
        self._content = content
        self._header = header

        self.content = Layout(
            Panel(Text.from_markup(content, justify="center"), title=header),
            name="content",
            ratio=8,
        )

        self.nav = Layout(name="navbar", ratio=2)

        self.base_layout.split_column(
            self.content,
            self.nav,
        )

        self._key_strokes_mappings = DEFAULT_KEY_BINDINGS

    def update_content(self, content: Any):
        self._content = content

        self.content.update(
            Layout(
                Panel(Text.from_markup(content, justify="center"), title=self._header),
                name="content",
                ratio=8,
            )
        )

    def blocking_selection_process(self) -> PAGE_EXIT_CODES:
        with Live(self.base_layout, auto_refresh=False):
            while True:
                next_char = _blocking_get_keystroke(self._key_strokes_mappings)

                if next_char == KEY_ACTIONS.QUIT:
                    return PAGE_EXIT_CODES.QUIT

                if next_char == KEY_ACTIONS.EXPAND:
                    return PAGE_EXIT_CODES.EXPAND

                if next_char == KEY_ACTIONS.UP:
                    return PAGE_EXIT_CODES.BACKWARD

                if next_char == KEY_ACTIONS.DOWN:
                    return PAGE_EXIT_CODES.FORWARD

                if next_char == KEY_ACTIONS.ENTER:
                    return PAGE_EXIT_CODES.ACTION

    def expand_view(self) -> None:
        console = Console()
        with console.pager():
            console.print(Text.from_markup(self._content))


class FinalInformationPage(InformationPage):
    def __init__(self, content: Any) -> None:
        super().__init__("REVIEW PAGE", content)
        self._is_completable = True

    def blocking_selection_process(self) -> PAGE_EXIT_CODES:
        with Live(self.base_layout, auto_refresh=False):
            while True:
                next_char = _blocking_get_keystroke(self._key_strokes_mappings)

                if next_char == KEY_ACTIONS.QUIT:
                    return PAGE_EXIT_CODES.QUIT

                if next_char == KEY_ACTIONS.EXPAND:
                    return PAGE_EXIT_CODES.EXPAND

                if next_char == KEY_ACTIONS.UP:
                    return PAGE_EXIT_CODES.BACKWARD

                if next_char == KEY_ACTIONS.DOWN:
                    return PAGE_EXIT_CODES.FORWARD

                if next_char == KEY_ACTIONS.ENTER:
                    if self._is_completable:
                        return PAGE_EXIT_CODES.ACTION

    def set_is_completable(self, is_completed: bool) -> None:
        self._is_completable = is_completed


class SelectionPage(Page):
    def get_selected_item(self) -> Any:
        raise NotImplementedError

    def get_selected_label(self) -> Any:
        raise NotImplementedError


class SimpleSelectionListPage(Page):
    def __init__(self, options: List[str]):
        super().__init__()
        self.data = options
        self._selected_item_index = 0
        self._key_strokes_mappings = DEFAULT_KEY_BINDINGS
        self._update_selection()

    def blocking_selection_process(self) -> str:
        with Live(self.base_layout, auto_refresh=False) as live:

            while True:
                next_char = _blocking_get_keystroke(self._key_strokes_mappings)

                if next_char == KEY_ACTIONS.DOWN:
                    self._move_selection(1)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.UP:
                    self._move_selection(-1)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.ENTER:
                    self.base_layout = ""
                    return self.data[self._selected_item_index]

    def _move_selection(self, increment: int):
        _tmp_index = (
            0
            if self._selected_item_index is None
            else increment + self._selected_item_index
        )

        if _tmp_index >= len(self.data) or _tmp_index < 0:
            return

        self._selected_item_index = _tmp_index
        self._update_selection()

    def _update_selection(self):
        _options_list = "\n".join(
            [
                x if i != self._selected_item_index else f"> {x}"
                for i, x in enumerate(self.data)
            ]
        )
        self.base_layout = Text.from_markup(_options_list)


class SingleItemSelectionPage(SelectionPage):
    def __init__(self, header: str, selection_data: single_item_selection_data) -> None:
        super().__init__()

        self.selection_data = selection_data
        self._selected_item_index = None

        self.header = Layout(
            Panel(Text.from_markup(header)),
            name="header",
            ratio=5,
        )

        self.content = Layout(
            Panel(Pretty(self.selection_data.content), title="Data"),
            name="content",
            ratio=10,
        )
        self.selection = Layout(name="content", ratio=1)

        self.nav = Layout(name="bottom", ratio=4)

        self.base_layout.split_column(
            self.header,
            self.selection,
            self.content,
            self.nav,
        )

        self._update_selection()

        self._key_strokes_mappings = DEFAULT_KEY_BINDINGS

    def blocking_selection_process(self) -> PAGE_EXIT_CODES:
        with Live(self.base_layout, auto_refresh=False) as live:

            while True:
                next_char = _blocking_get_keystroke(self._key_strokes_mappings)

                if next_char == KEY_ACTIONS.RIGHT:
                    self._move_selection(1)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.LEFT:
                    self._move_selection(-1)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.QUIT:
                    return PAGE_EXIT_CODES.QUIT

                if next_char == KEY_ACTIONS.EXPAND:
                    return PAGE_EXIT_CODES.EXPAND

                if next_char == KEY_ACTIONS.UP:
                    return PAGE_EXIT_CODES.BACKWARD

                if next_char == KEY_ACTIONS.DOWN:
                    return PAGE_EXIT_CODES.FORWARD

                if next_char == KEY_ACTIONS.ENTER:
                    return PAGE_EXIT_CODES.FORWARD

    def expand_view(self) -> None:
        console = Console()
        with console.pager():
            console.print("++++++++++++++++DATA++++++++++++++++")
            console.print(Pretty(self.selection_data.content, expand_all=True))
            console.print("+++++++++++++++++++++++++++++++++++++++")

    def _move_selection(self, increment: int):
        _tmp_index = (
            0
            if self._selected_item_index is None
            else increment + self._selected_item_index
        )

        if _tmp_index >= len(self.selection_data.options) or _tmp_index < 0:
            return

        self._selected_item_index = _tmp_index
        self._update_selection()

    def _update_selection(self):

        _options_list = [x[0] for x in self.selection_data.options]

        if not self._selected_item_index is None:
            _options_list[
                self._selected_item_index
            ] = f"[bold reverse cyan]{_options_list[self._selected_item_index]}[/bold reverse cyan]"

        _options = " | ".join(_options_list)
        self.selection.update((f"{_options}"))

    def get_selected_item(self) -> Any:
        if self._selected_item_index is None:
            return None

        return self.selection_data.options[self._selected_item_index][1]

    def get_selected_label(self) -> Any:
        if self._selected_item_index is None:
            return None

        return self.selection_data.options[self._selected_item_index][0]


class TwoItemSelectionPage(SelectionPage):
    def __init__(self, header: str, selection_data: two_item_selection_data) -> None:
        super().__init__()

        self.selection_data = selection_data
        self.header = Layout(
            Panel(Text.from_markup(header)),
            name="header",
            ratio=5,
        )

        self.subheader = TwoItemSelectionPage._make_split_pane(
            name="subheader", ratio=1
        )
        self.content = TwoItemSelectionPage._make_split_pane(name="content", ratio=10)

        self.nav = Layout(name="nav", ratio=4)

        self.base_layout.split_column(
            self.header,
            self.subheader.base,
            self.content.base,
            self.nav,
        )

        self.subheader.left.update(
            Text.from_markup(self.selection_data.left_data.header)
        )
        self.subheader.right.update(
            Text.from_markup(self.selection_data.right_data.header)
        )

        self.content.left.update(
            self._create_content_panel(selection_data.left_data.content)
        )
        self.content.right.update(
            self._create_content_panel(selection_data.right_data.content)
        )

        self.is_left_selected = None

        self._key_strokes_mappings = DEFAULT_KEY_BINDINGS

    def blocking_selection_process(self) -> PAGE_EXIT_CODES:
        with Live(self.base_layout, auto_refresh=False) as live:
            while True:
                next_char = _blocking_get_keystroke(self._key_strokes_mappings)

                if next_char == KEY_ACTIONS.RIGHT:
                    self._select_side(select_left=False)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.LEFT:
                    self._select_side(select_left=True)
                    live.update(self.base_layout, refresh=True)

                if next_char == KEY_ACTIONS.QUIT:
                    return PAGE_EXIT_CODES.QUIT

                if next_char == KEY_ACTIONS.EXPAND:
                    return PAGE_EXIT_CODES.EXPAND

                if next_char == KEY_ACTIONS.UP:
                    return PAGE_EXIT_CODES.BACKWARD

                if next_char == KEY_ACTIONS.DOWN:
                    return PAGE_EXIT_CODES.FORWARD

                if next_char == KEY_ACTIONS.ENTER:
                    return PAGE_EXIT_CODES.FORWARD

    def expand_view(self) -> None:
        console = Console()
        with console.pager():
            console.print("+++++++++++++++++++++++++++++++++++++++")
            console.print(self.selection_data.left_data.header)
            console.print("+++++++++++++++++++++++++++++++++++++++")
            console.print(
                Pretty(self.selection_data.left_data.content, expand_all=True)
            )

            console.print("")
            console.print("+++++++++++++++++++++++++++++++++++++++")
            console.print(self.selection_data.right_data.header)
            console.print("+++++++++++++++++++++++++++++++++++++++")
            console.print(
                Pretty(self.selection_data.right_data.content, expand_all=True)
            )

    def _select_side(self, select_left: bool):
        if select_left == self.is_left_selected:
            return

        if self.is_left_selected is None:
            self.is_left_selected = not select_left

        if not select_left and self.is_left_selected:
            self.subheader.left.update(
                Text.from_markup(self.selection_data.left_data.header)
            )
            self.subheader.right.update(
                Text.from_markup(
                    f"[reverse cyan]{self.selection_data.right_data.header}[/reverse cyan]"
                )
            )

            self.content.left.update(
                self._create_content_panel(self.selection_data.left_data.content)
            )
            self.content.right.update(
                self._create_content_panel(
                    self.selection_data.right_data.content, is_selected=True
                )
            )

        if select_left and not self.is_left_selected:
            self.subheader.left.update(
                Text.from_markup(
                    f"[reverse cyan]{self.selection_data.left_data.header}[/reverse cyan]"
                )
            )
            self.subheader.right.update(
                Text.from_markup(self.selection_data.right_data.header)
            )

            self.content.left.update(
                self._create_content_panel(
                    self.selection_data.left_data.content, is_selected=True
                )
            )
            self.content.right.update(
                self._create_content_panel(self.selection_data.right_data.content)
            )

        self.is_left_selected = select_left

    def _make_split_pane(name: str, ratio: int = None) -> split_layout:
        base_layout = Layout(name=name, ratio=ratio) if ratio else Layout(name=name)

        right = Layout(name=f"{name}-right")
        left = Layout(name=f"{name}-left")

        base_layout.split_row(
            left,
            right,
        )

        return split_layout(base=base_layout, right=right, left=left)

    def _create_content_panel(self, data: Any, is_selected: bool = False) -> Panel:
        _border_style = "bold" if is_selected else "dim"
        return Panel(Pretty(data), border_style=_border_style)

    def get_selected_item(self) -> Any:
        if self.is_left_selected is None:
            return None

        return (
            self.selection_data.left_data.rv
            if self.is_left_selected
            else self.selection_data.right_data.rv
        )

    def get_selected_label(self) -> Any:
        if self.is_left_selected is None:
            return None

        return (
            self.selection_data.left_data.header
            if self.is_left_selected
            else self.selection_data.right_data.header
        )


class SelectionPageContainer:
    def __init__(
        self, quit_title: str, quit_content: str, quit_navbar: str = None
    ) -> None:
        self.pages: List[Page] = []
        self._current_index = 0
        self._final_page: FinalInformationPage = None
        self._quit_page = InformationPage(quit_title, quit_content)

        self._quit_page.update_navigation_bar(
            Panel(
                Text.from_markup(quit_navbar, justify="center"),
                title=f"NAVIGATION",
                title_align="center",
            )
        )

    def add_page(self, page: Page) -> None:
        self.pages.append(page)

    def _generate_nav_characters(self, page: Page) -> str:

        if isinstance(page, SelectionPage):
            return (
                PAGE_NAV_EMOJIS.INCOMPLETE.value
                if page.get_selected_item() is None
                else PAGE_NAV_EMOJIS.COMPLETE.value
            )

        else:
            return PAGE_NAV_EMOJIS.INFORMATION.value

    def _get_current_nav_panel(self) -> Panel:

        _base_nav_characters = [
            self._generate_nav_characters(x)
            if indx == self._current_index
            else f"[dim]{self._generate_nav_characters(x)}[/dim]"
            for indx, x in enumerate(self.pages)
        ]

        _nav_str = " ".join(_base_nav_characters)

        nav_content = f"""[bold yellow]up-arrow[/bold yellow]: Previous Page; [bold yellow]down-arrow[/bold yellow]: Next Page; [bold yellow]q[/bold yellow]: Quit; [bold yellow]e[/bold yellow]: Expand

{_nav_str} ({self._current_index+1}/{len(self.pages)})
        """

        return Panel(
            Text.from_markup(nav_content, justify="center"),
            title=f"NAVIGATION",
            title_align="center",
        )

    def _update_final_page(self) -> None:
        _results = self.get_results()
        is_completed = all(_results)

        self._final_page.set_is_completable(is_completed)

        _selection_str = "\n".join(
            f"page {i+1} -> {f'[blue]{x}[/blue]' if x else '[red]No Selection. Return to page to complete.[/red]'}"
            for i, x in enumerate(self.get_result_labels())
        )

        if is_completed:
            self._final_page.update_content(
                FINAL_PAGE_COMPLETE_TEMPLATE.format(selections=_selection_str)
            )
        else:
            self._final_page.update_content(
                FINAL_PAGE_INCOMPLETE_TEMPLATE.format(selections=_selection_str)
            )

    def _get_final_page(self) -> Page:
        if self._final_page:
            return self._final_page

        self._final_page = FinalInformationPage("Review your selections")

        return self._final_page

    def run_pages(self) -> None:
        self.add_page(self._get_final_page())
        while True:
            if self._current_index == len(self.pages) - 1:
                self._update_final_page()

            _current_page = self.pages[self._current_index]

            _current_page.update_navigation_bar(self._get_current_nav_panel())
            exit_code = _current_page.blocking_selection_process()

            if exit_code == PAGE_EXIT_CODES.QUIT:
                quit_rv = self._quit_page.blocking_selection_process()

                if quit_rv == PAGE_EXIT_CODES.QUIT:
                    raise DidNotCompleteSelections

            elif exit_code == PAGE_EXIT_CODES.BACKWARD:
                if self._current_index > 0:
                    self._current_index -= 1

            elif exit_code == PAGE_EXIT_CODES.FORWARD:
                if self._current_index < len(self.pages) - 1:
                    self._current_index += 1

            elif exit_code == PAGE_EXIT_CODES.EXPAND:
                _current_page.expand_view()

            elif exit_code == PAGE_EXIT_CODES.ACTION:
                if self._current_index == len(self.pages) - 1:
                    return

    def get_results(self) -> List[Any]:
        return [
            page.get_selected_item()
            for page in self.pages
            if isinstance(page, SelectionPage)
        ]

    def get_result_labels(self) -> List[Any]:
        return [
            page.get_selected_label()
            for page in self.pages
            if isinstance(page, SelectionPage)
        ]


def _blocking_get_keystroke(mapping: Dict[Any, KEY_ACTIONS] = None) -> KEY_ACTIONS:
    fd = sys.stdin.fileno()
    # save settings from the tty session
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.buffer.read1(3)  # This number represents the length

    finally:
        # reset settings from the tty session
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return mapping.get(ch) if mapping else ch
