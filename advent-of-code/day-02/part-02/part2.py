import itertools
import functools
from pathlib import Path
from typing import Annotated

import typer
import structlog

import gameparser

APP = typer.Typer()

LOG = structlog.get_logger()


def get_game_power(game: gameparser.GameRound) -> int:
    colour_minimums = {
        gameparser.Colour.red: 0,
        gameparser.Colour.blue: 0,
        gameparser.Colour.green: 0,
    }
    for game_round in game["reveals"]:
        for reveal in game_round:
            colour = reveal["colour"]
            colour_minimums[colour] = max(colour_minimums[colour], reveal["count"])
    minimums = list(colour_minimums.values())
    return minimums[0] * minimums[1] * minimums[2]


@APP.command()
def main(
    input: Path,
    expected: int = -1,
):
    parsed = gameparser.parse(input.open("r").read())
    LOG.debug("parsed", parsed=parsed)

    total = 0
    for game in parsed:
        LOG.info(game)
        total += get_game_power(game)
    LOG.info("total", total=total)
    if expected > 0 and total != expected:
        LOG.warning("wrong expected total", expected=expected, total=total)


if __name__ == "__main__":
    APP()
