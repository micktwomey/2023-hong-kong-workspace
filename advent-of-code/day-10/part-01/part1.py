from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Optional, DefaultDict, Annotated

from pydantic import BaseModel, Field
import typer
import structlog

app = typer.Typer()
LOG = structlog.get_logger()

"""
| is a vertical pipe connecting north and south.
- is a horizontal pipe connecting east and west.
L is a 90-degree bend connecting north and east.
J is a 90-degree bend connecting north and west.
7 is a 90-degree bend connecting south and west.
F is a 90-degree bend connecting south and east.
. is ground; there is no pipe in this tile.
S is the starting position of the animal; there is a pipe on this tile, but your sketch doesn't show what shape the pipe has.
"""
SOURCE_TO_GRAPHIC = {
    "|": "║",
    "-": "═",
    "L": "╚",
    "J": "╝",
    "7": "╗",
    "F": "╔",
    ".": ".",
    "S": "S",
    "\n": "\n",
}

CONNECTION_TO_DIRECTION = {
    0: "N",
    1: "E",
    2: "S",
    3: "W",
}

CONNECTABLE = {
    "N": {"S", "║", "╗", "╔"},
    "S": {"S", "║", "╚", "╝"},
    "E": {"S", "═", "╝", "╗"},
    "W": {"S", "═", "╚", "╔"},
}

DIRECTION_TO_CONNECTION = {
    "N": 0,
    "E": 1,
    "S": 2,
    "W": 3,
}


class Tile(BaseModel):
    x: int
    y: int
    source: str
    graphic: str
    connections: list[
        Optional[tuple[int, int]]
    ]  # connected tiles, 0: N, 1: E, 2: S, 3: W

    def add_north_connection(self, map: "Map"):
        other = map.tiles[self.x].get(self.y - 1, None)
        if (
            other is not None
            and (other.graphic in CONNECTABLE["N"])
            and (self.graphic in CONNECTABLE["S"])
        ):
            other.connections[DIRECTION_TO_CONNECTION["S"]] = (self.x, self.y)
            self.connections[DIRECTION_TO_CONNECTION["N"]] = (other.x, other.y)

    def add_south_connection(self, map: "Map"):
        other = map.tiles[self.x].get(self.y + 1, None)
        if (
            other is not None
            and (other.graphic in CONNECTABLE["S"])
            and (self.graphic in CONNECTABLE["N"])
        ):
            other.connections[DIRECTION_TO_CONNECTION["N"]] = (self.x, self.y)
            self.connections[DIRECTION_TO_CONNECTION["S"]] = (other.x, other.y)

    def add_east_connection(self, map: "Map"):
        other = map.tiles.get(self.x + 1, {}).get(self.y, None)
        if (
            other is not None
            and (other.graphic in CONNECTABLE["E"])
            and (self.graphic in CONNECTABLE["W"])
        ):
            other.connections[DIRECTION_TO_CONNECTION["W"]] = (self.x, self.y)
            self.connections[DIRECTION_TO_CONNECTION["E"]] = (other.x, other.y)

    def add_west_connection(self, map: "Map"):
        other = map.tiles.get(self.x - 1, {}).get(self.y, None)
        if (
            other is not None
            and (other.graphic in CONNECTABLE["W"])
            and (self.graphic in CONNECTABLE["E"])
        ):
            other.connections[DIRECTION_TO_CONNECTION["E"]] = (self.x, self.y)
            self.connections[DIRECTION_TO_CONNECTION["W"]] = (other.x, other.y)


class Animal(BaseModel):
    x: int
    y: int
    previous: Tile
    distance_travelled: int = 0
    graphic: str = "A"


Tiles = DefaultDict[int, Annotated[dict[int, Tile], Field(default_factory=dict)]]


class Map(BaseModel):
    tiles: Tiles
    width: int
    height: int
    start_tile: Tile | None = None

    def update_start_tile(self):
        for row in self.tiles.values():
            for tile in row.values():
                if tile.graphic == "S":
                    self.start_tile = tile

    def update_connections(self):
        for row in self.tiles.values():
            for tile in row.values():
                match tile.graphic:
                    case "║":
                        tile.add_north_connection(self)
                        tile.add_south_connection(self)
                    case "═":
                        tile.add_west_connection(self)
                        tile.add_east_connection(self)
                    case "╚":
                        tile.add_north_connection(self)
                        tile.add_east_connection(self)
                    case "╝":
                        tile.add_north_connection(self)
                        tile.add_west_connection(self)
                    case "╗":
                        tile.add_west_connection(self)
                        tile.add_south_connection(self)
                    case "╔":
                        tile.add_east_connection(self)
                        tile.add_south_connection(self)
                    case ".":
                        pass
                    case "S":
                        tile.add_north_connection(self)
                        tile.add_south_connection(self)
                        tile.add_east_connection(self)
                        tile.add_west_connection(self)
                        self.start_tile = tile
                    case _:
                        raise NotImplementedError(tile)


class Solution(BaseModel):
    map: Map
    animals: list[Animal]

    def get_map_as_markup(self) -> str:
        map: list[str] = []
        previous_y = 0
        for y in range(self.map.height):
            for x in range(self.map.width):
                if y > previous_y:
                    map.append("\n")
                    previous_y = y
                map.append(self.map.tiles[x][y].graphic)
        return "".join(map)

    def stepper(self):
        yield 1


@app.command()
def pretty_print_input(input: Path):
    map = parse(input.open("r").read())
    # for char in input.open("r").read():
    previous_y = 0
    for y in range(map.height):
        for x in range(map.width):
            if y > previous_y:
                sys.stdout.write("\n")
                previous_y = y
            sys.stdout.write(map.tiles[x][y].graphic)

    print()
    map.update_connections()
    print(map.start_tile)


def parse(input: str) -> Map:
    map = Map(tiles=defaultdict(dict), width=0, height=0)
    x = 0
    y = 0
    for char in input:
        if char == "\n":
            x = 0
            y += 1
            continue
        map.tiles[x][y] = Tile(
            x=x,
            y=y,
            source=char,
            graphic=SOURCE_TO_GRAPHIC[char],
            connections=[None, None, None, None],
        )
        map.width = max(map.width, x + 1)
        map.height = max(map.height, y + 1)
        x += 1
    return map


@app.command()
def dump_map(input: Path):
    map = parse(input.open("r").read())
    map.update_connections()
    sys.stdout.write(map.model_dump_json())


if __name__ == "__main__":
    app()
