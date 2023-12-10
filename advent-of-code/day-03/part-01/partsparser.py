from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
import re
from typing import Iterable

import structlog

LOG = structlog.get_logger()


@dataclass
class Digit:
    digit: str
    x: int
    y: int

    def neighbours(self) -> Iterable[tuple[int, int]]:
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                coord = (self.x + x_offset, self.y + y_offset)
                if coord != (self.x, self.y):
                    yield coord


@dataclass
class Number:
    digits: list[Digit]

    @cached_property
    def value(self) -> int:
        s = "".join(d.digit for d in self.digits)
        return int(s)

    def neighbours(self) -> Iterable[tuple[int, int]]:
        selves = set((d.x, d.y) for d in self.digits)
        coords = set()
        for d in self.digits:
            coords.update(d.neighbours())
        for coord in coords.difference(selves):
            yield coord


@dataclass
class Part:
    symbol: str


Squares = dict[int, dict[int, Digit | None | Part]]


@dataclass
class Grid:
    squares: Squares
    numbers: list[Number]
    width: int = 0

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


def parts_parser(input: list[str]) -> Grid:
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
    grid = Grid(squares=defaultdict(dict), numbers=[])
    current_number: Number | None = None
    for y, line in enumerate(input):
        for x, char in enumerate(line):
            if re.match(r"[0-9]", char):
                digit = Digit(digit=char, x=x, y=y)
                if current_number is None:
                    current_number = Number(digits=[digit])
                else:
                    current_number.digits.append(digit)
                square = digit
            elif char == ".":
                square = None
                if current_number is not None:
                    grid.numbers.append(current_number)
                    current_number = None
            elif re.match(r"[^0-9.]", char):
                part = Part(symbol=char)
                square = part
                if current_number is not None:
                    grid.numbers.append(current_number)
                    current_number = None
            else:
                raise NotImplementedError(char)

            grid.squares[x][y] = square
    return grid
