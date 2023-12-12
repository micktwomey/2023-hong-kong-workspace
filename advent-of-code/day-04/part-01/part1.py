from pathlib import Path

import cardparser
import structlog
import typer

APP = typer.Typer()
LOG = structlog.get_logger()


@APP.command()
def main(
    input: Path,
    expected: int = -1,
):
    parsed = cardparser.parse(input.open("r").read())
    LOG.debug("parsed", parsed=parsed)

    total = 0
    for row in parsed:
        winners = row["winning_numbers"].intersection(row["numbers"])
        points = 1 if winners else 0
        [points := points * 2 for _ in range(len(winners) - 1)]
        LOG.info(row, winners=winners, points=points)
        total += points
    LOG.info("total", total=total)
    if expected > 0 and total != expected:
        LOG.warning("wrong expected total", expected=expected, total=total)


if __name__ == "__main__":
    APP()
