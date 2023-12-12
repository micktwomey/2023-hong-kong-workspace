from pathlib import Path

import typer
from solution import Solution
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Header, Static

from rich.text import Text

CLI = typer.Typer()


class Map(Widget):
    DEFAULT_CSS = """
    Map > Static {
        height: auto;
        width: auto;
    }
    """

    class TotalUpdated(Message):
        def __init__(self, total: int):
            self.total = total
            super().__init__()

    def __init__(self, solution: Solution, *args, **kwargs):
        self.solution = solution
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        # line = []
        # for i in range(20):
        #     line.append(f".*..........[i]{i:02}[/]")
        # line = "".join(line)
        # print((len(line), line))
        # lines = []
        # for i in range(140):
        #     lines.append(f"[b]{i:03}[/b]{line}")
        # lines = "\n".join(lines)
        # lines = open("input", "r").read()
        # self.solution.grid.squares[0][1].processing = True
        # self.solution.grid.squares[0][0].matched = True
        self.total = 0
        lines = self.solution.get_map_as_markup()
        self.map = Static(lines)
        self.stepper = self.solution.stepper()
        yield self.map

    def step(self) -> None:
        try:
            self.total = next(self.stepper)
        except StopIteration:
            pass
        self.update_map()

    def update_map(self) -> None:
        self.map.update(Text.from_markup(self.solution.get_map_as_markup()))
        self.post_message(self.TotalUpdated(self.total))
        self.map.refresh()

    def run(self) -> None:
        for total in self.stepper:
            self.total = total
        self.update_map()


class MapScreen(Screen):
    DEFAULT_CSS = """
    #map {
        overflow: scroll scroll;
    }
    """

    def __init__(self, solution: Solution, *args, **kwargs):
        self.solution = solution
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ScrollableContainer(id="map-scrollable-container"):
            yield Map(self.solution, id="map")


@CLI.command()
def main(input: Path):
    solution = Solution(input)

    class SolutionApp(App):
        BINDINGS = [
            Binding(key="q", action="quit", description="Quit the app"),
            Binding(key="s", action="step", description="Step the solution"),
            Binding(key="r", action="run", description="Run the solution"),
        ]

        def on_ready(self) -> None:
            self.push_screen(MapScreen(solution))

        def on_mount(self) -> None:
            self.total = 0
            self.title = "Day 3 Part 2"
            self.sub_title = f"Total = {self.total}"

        def action_step(self) -> None:
            map = self.query_one(Map)
            map.step()

        def action_run(self) -> None:
            map = self.query_one(Map)
            map.run()

        def on_map_total_updated(self, message: Map.TotalUpdated):
            self.total = message.total
            self.sub_title = f"Total = {self.total}"

    app = SolutionApp()
    app.run()


if __name__ == "__main__":
    CLI()
