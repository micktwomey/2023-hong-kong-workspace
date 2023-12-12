from pathlib import Path

import typer
import structlog

import partsparser

APP = typer.Typer()

LOG = structlog.get_logger()


@APP.command()
def main(input: Path, expected: int = -1, greater_than: int = -1):
    grid = partsparser.parts_parser(
        input=(line.strip() for line in input.open("r").readlines() if line.strip())
    )

    ratios: list[int] = []
    for _, _, square in grid.iterate_squares():
        match square:
            case partsparser.Part(symbol="*"):
                numbers: set[int] = set()
                for neighbour in grid.iterate_neighbours(square):
                    match neighbour:
                        case partsparser.Digit():
                            numbers.add(neighbour.number.value)

                ratio = None
                numbers = list(numbers)
                if len(numbers) == 2:
                    n1 = numbers[0]
                    n2 = numbers[1]
                    ratio = n1 * n2
                    ratios.append(ratio)
                LOG.info("gear", part=square, numbers=numbers, ratio=ratio)

    total = sum(ratios)
    LOG.info("total", total=total)
    if expected > 0 and expected != total:
        LOG.warning("Total incorrect", total=total, expected=expected)
    if greater_than > 0 and greater_than >= total:
        LOG.warning("Total incorrect", total=total, greater_than=greater_than)


if __name__ == "__main__":
    APP()
