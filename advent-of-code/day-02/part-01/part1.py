from pathlib import Path
from typing import Annotated

import typer
import structlog

import gameparser

APP = typer.Typer()

LOG = structlog.get_logger()


def get_game_amount(
    game: gameparser.GameRound, max_possible: dict[gameparser.Colour, int]
) -> int:
    possible = True
    for game_round in game["reveals"]:
        for reveal in game_round:
            if reveal["count"] > max_possible[reveal["colour"]]:
                possible = False
    if possible:
        return game["game"]
    return 0


@APP.command()
def main(
    input: Path,
    expected: int = -1,
    max_red: int = 0,
    max_green: int = 0,
    max_blue: int = 0,
):
    parsed = gameparser.parse(input.open("r").read())
    LOG.debug("parsed", parsed=parsed)

    total = 0
    for game in parsed:
        LOG.info(game)
        total += get_game_amount(
            game,
            {
                gameparser.Colour.red: max_red,
                gameparser.Colour.blue: max_blue,
                gameparser.Colour.green: max_green,
            },
        )
    LOG.info("total", total=total)
    if expected > 0 and total != expected:
        LOG.warning("wrong expected total", expected=expected, total=total)


if __name__ == "__main__":
    APP()
