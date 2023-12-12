"""Event driven solution :)

"""
import collections

from pathlib import Path

import partsparser


def get_markup(square: partsparser.Square) -> str:
    char = "?"
    match square:
        case partsparser.Empty():
            char = "."
        case partsparser.Digit():
            char = square.digit
        case partsparser.Part():
            char = square.symbol
        case _:
            raise NotImplementedError(square)
    styles = []
    if square.matched:
        styles.append("bold green")
    if square.processing:
        styles.append("on blue")
    styles = " ".join(styles)
    opening = f"[{styles}]" if styles else ""
    closing = "[/]" if styles else ""
    print((square.x, square.y, opening, closing))
    return f"{opening}{char}{closing}"


class Solution:
    def __init__(self, input: Path):
        self.grid = partsparser.parts_parser(
            input=(line.strip() for line in input.open("r").readlines() if line.strip())
        )
        self.ratios: list[int] = []
        self.total = 0

    def get_map_as_markup(self) -> str:
        rows: dict[int, list[str]] = collections.defaultdict(list)
        lines = []
        for x, y, square in self.grid.iterate_squares():
            rows[y].append(get_markup(square))
        for row in rows.values():
            lines.append("".join(row))
        return "\n".join(lines)

    def stepper(self):
        ratios: list[int] = []
        previous_square: partsparser.Square | None = None
        for _, _, square in self.grid.iterate_squares():
            square.processing = True
            if previous_square is not None:
                print((previous_square, square))
                previous_square.processing = False
            previous_square = square

            match square:
                case partsparser.Part(symbol="*"):
                    numbers: dict[tuple(int, int), partsparser.Number] = {}
                    for neighbour in self.grid.iterate_neighbours(square):
                        match neighbour:
                            case partsparser.Digit():
                                neighbour.number.processing = True
                                number = neighbour.number
                                numbers[(number.x, number.y)] = number

                    ratio = None
                    if len(numbers) == 2:
                        for number in numbers.values():
                            number.matched = True
                        square.matched = True
                        values = list(n.value for n in numbers.values())
                        n1 = values[0]
                        n2 = values[1]
                        ratio = n1 * n2
                        ratios.append(ratio)

                    self.total = sum(ratios)
                    yield self.total
