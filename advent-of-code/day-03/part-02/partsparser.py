from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
import re
from typing import Iterable, Union

import structlog

LOG = structlog.get_logger()


def find_neighbours(square: "Square", grid: "Grid") -> Iterable["Square"]:
    for x, y in square.neighbours():
        neighbour = grid.squares.get(x, {}).get(y, None)
        if neighbour is not None:
            yield neighbour


@dataclass
class Empty:
    x: int
    y: int
    processing: bool = False
    matched: bool = False


@dataclass
class Digit:
    digit: str
    x: int
    y: int
    number: Union["Number", None] = None
    processing: bool = False
    matched: bool = False

    def neighbours(self) -> Iterable[tuple[int, int]]:
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                coord = (self.x + x_offset, self.y + y_offset)
                if coord != (self.x, self.y):
                    yield coord


@dataclass()
class Number:
    digits: list[Digit]
    processing: bool = False

    @cached_property
    def value(self) -> int:
        s = "".join(d.digit for d in self.digits)
        return int(s)

    def neighbours(self) -> Iterable[tuple[int, int]]:
        selves: set[tuple[int, int]] = set((d.x, d.y) for d in self.digits)
        coords: set[tuple[int, int]] = set()
        for d in self.digits:
            coords.update(d.neighbours())
        for coord in coords.difference(selves):
            yield coord

    def update_digit_references(self) -> None:
        for digit in self.digits:
            digit.number = self

    @property
    def matched(self):
        return all(d.matched for d in self.digits)

    @matched.setter
    def matched(self, value):
        for digit in self.digits:
            digit.matched = value

    @property
    def x(self):
        return min(d.x for d in self.digits)

    @property
    def y(self):
        return min(d.y for d in self.digits)


@dataclass
class Part:
    symbol: str
    x: int
    y: int
    processing: bool = False
    matched: bool = False

    def neighbours(self) -> Iterable[tuple[int, int]]:
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                coord = (self.x + x_offset, self.y + y_offset)
                if coord != (self.x, self.y):
                    yield coord


Square = Digit | Part | Empty
Squares = dict[int, dict[int, Square]]


@dataclass
class Grid:
    squares: Squares
    numbers: list[Number]
    parts: list[Part]

    def get_part_numbers(self) -> Iterable[tuple[int, bool]]:
        for number in self.numbers:
            LOG.info("number", number=number)
            for x, y in number.neighbours():
                try:
                    square = self.squares[x][y]
                except KeyError:
                    continue
                LOG.info("neighbour", x=x, y=y, square=square)
                is_part = False
                match square:
                    case Part():
                        is_part = True
                    case _:
                        continue
                yield (number.value, is_part)

    def iterate_squares(self) -> Iterable[tuple[int, int, Part | Digit]]:
        for x, row in self.squares.items():
            for y, square in row.items():
                if square is not None:
                    yield (x, y, square)

    def iterate_neighbours(self, square: Digit | Part) -> Iterable[Part | Digit]:
        yield from find_neighbours(square, self)


def parts_parser(input: Iterable[str]) -> Grid:
    """

    Example:

        467..114..
        ...*......
        ..35..633.
        ......#...
        617*......
        .....+.58.
        ..592.....
        ......755.
        ...$.*....
        .664.598..

    Parse into a grid with digits, dots or symbols.

    """
    grid = Grid(squares=defaultdict(dict), numbers=[], parts=[])
    current_number: Number | None = None
    for y, line in enumerate(input):
        for x, char in enumerate(line):
            square: Part | Digit | None
            if re.match(r"[0-9]", char):
                digit = Digit(digit=char, x=x, y=y)
                if current_number is None:
                    current_number = Number(digits=[digit])
                else:
                    current_number.digits.append(digit)
                square = digit
            elif char == ".":
                square = Empty(x=x, y=y)
                if current_number is not None:
                    current_number.update_digit_references()
                    grid.numbers.append(current_number)
                    current_number = None
            elif re.match(r"[^0-9.]", char):
                part = Part(symbol=char, x=x, y=y)
                square = part
                grid.parts.append(part)
                if current_number is not None:
                    current_number.update_digit_references()
                    grid.numbers.append(current_number)
                    current_number = None
            else:
                raise NotImplementedError(char)

            grid.squares[x][y] = square
    width = len(grid.squares)
    height = len(grid.squares[0])
    assert width == height
    return grid
