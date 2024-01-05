from pathlib import Path

import typer
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Grid
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Header, Static, Placeholder, Log

from rich.text import Text

import part1

CLI = typer.Typer()


class InfoPanel(Widget):
    DEFAULT_CSS = """
    InfoPanel {
        layout: grid;
        grid-size: 3 3;
        grid-rows: 1fr;
        grid-columns: 1fr 1fr 1fr 1fr 1fr;
        grid-gutter: 1;
    }
    #n {
        column-span: 3;
    }
    #s {
        column-span: 3;
    }
    #coord {
        text-align: center;
    }
    """

    class InfoUpdated(Message):
        def __init__(
            self,
            north: bool,
            south: bool,
            east: bool,
            west: bool,
            graphic: str,
            coordinate: tuple[int, int],
        ):
            self.north = north
            self.south = south
            self.east = east
            self.west = west
            self.graphic = graphic
            self.coordinate = coordinate
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Placeholder("N", id="n")
        yield Placeholder("W", id="w")
        yield Placeholder("╝\n(10,20)", id="status")
        yield Placeholder("E", id="e")
        yield Placeholder("S", id="s")


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

    def __init__(self, solution: part1.Solution, *args, **kwargs):
        self.solution = solution
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
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
    MapScreen {
        layout: grid;
        grid-size: 2 1;
        grid-rows: 1fr;
        grid-columns: 9fr 2fr;
        grid-gutter: 1;
    }
    """

    def __init__(self, solution: part1.Solution, *args, **kwargs):
        self.solution = solution
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        # with Grid():
        with ScrollableContainer(id="map-scrollable-container"):
            yield Map(self.solution, id="map")
        with Grid():
            yield InfoPanel()
            yield Log()


@CLI.command()
def main(input: Path):
    map = part1.parse(input.open("r").read())
    solution = part1.Solution(map=map, animals=[])

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
            self.title = "Day 10 Part 1"
            self.sub_title = f"Steps = {self.total}"

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
