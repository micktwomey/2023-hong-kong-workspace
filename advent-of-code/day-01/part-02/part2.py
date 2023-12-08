import re
import sys

import structlog

LOG = structlog.get_logger()


LOOKUP = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "zero": "0",
}


def main():
    numbers: list[int] = []
    for line in sys.stdin:
        matches = [
            x
            for x in re.findall(
                r"([0-9]|one|two|three|four|five|six|seven|eight|nine|zero)",
                line,
            )
            if x
        ]
        first = LOOKUP.get(matches[0], matches[0])
        last = LOOKUP.get(matches[-1], matches[-1])
        number = int(f"{first}{last}")
        numbers.append(number)
        LOG.info((line, matches, first, last, number))
    LOG.info("total", total=sum(numbers))


if __name__ == "__main__":
    main()
