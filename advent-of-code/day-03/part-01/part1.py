from pathlib import Path

import typer
import structlog

import partsparser

APP = typer.Typer()

LOG = structlog.get_logger()


@APP.command()
def main(input: Path, expected: int = -1):
    grid = partsparser.parts_parser(
        input=(line.strip() for line in input.open("r").readlines() if line.strip())
    )
    LOG.info("parsed", grid=grid)

    for y, row in grid.squares.items():
        print((y, row))

    part_numbers = []
    for number, is_part in grid.get_part_numbers():
        LOG.info("part?", number=number, is_part=is_part)
        if is_part:
            part_numbers.append(number)

    total = sum(part_numbers)
    LOG.info("total", total=total)
    if expected > 0 and expected != total:
        LOG.warning("Total incorrect", total=total, expected=expected)


if __name__ == "__main__":
    APP()
