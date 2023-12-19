import json
import sys
from pathlib import Path

import parsy
import structlog
import tqdm
import typer

app = typer.Typer()
LOG = structlog.get_logger()


EXAMPLE = """0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
"""

EXAMPLE2 = """4 -1 -6 -11 -16
"""

VALUE = parsy.regex(r"-{0,1}[0-9]+").map(int)
HISTORY = VALUE.sep_by(parsy.string(" "))
HISTORIES = HISTORY.sep_by(parsy.string("\n"))


def parse(input: str) -> list[list[int]]:
    return [h for h in HISTORIES.parse(input) if h]


assert parse(EXAMPLE) == [
    [0, 3, 6, 9, 12, 15],
    [1, 3, 6, 10, 15, 21],
    [10, 13, 16, 21, 30, 45],
], parse(EXAMPLE)

assert parse(EXAMPLE2) == [[4, -1, -6, -11, -16]], parse(EXAMPLE2)


@app.command()
def parse_to_json(input: Path):
    parsed = parse(input.open("r").read())
    json.dump(parsed, sys.stdout)


@app.command()
def solution(input: Path):
    parsed = parse(input.open("r").read())
    total = 0
    for history in parsed:
        # print(" ".join(str(i) for i in history))
        deltas: list[list[int]] = [history]
        unsolved = True
        i = 0
        while unsolved:
            i += 1
            new_deltas: list[int] = [
                deltas[-1][n] - deltas[-1][n - 1] for n in range(1, len(deltas[-1]))
            ]

            # assert len(new_deltas) == (len(deltas[-1]) - 1)
            if set(new_deltas) == {0}:
                unsolved = False
            deltas.append(new_deltas)

        current = 0
        for line in reversed(deltas):
            line.append(line[-1] + current)
            current = line[-1]

        for i, line in enumerate(deltas):
            print(i * " " + " ".join(str(i) for i in line))
        print()

        total += deltas[0][-1]
        print(f"Total: {total}\n")


if __name__ == "__main__":
    app()
