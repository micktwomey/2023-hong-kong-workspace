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


def get_matches(s: str) -> list[str]:
    return [
        x
        for x in re.findall(
            r"(?=([0-9]|one|two|three|four|five|six|seven|eight|nine|zero))",  # find overlapping matches, see https://stackoverflow.com/questions/11430863/how-to-find-overlapping-matches-with-a-regexp
            # r"([0-9]|one|two|three|four|five|six|seven|eight|nine|zero)",
            s,
        )
        if x
    ]


def main():
    numbers: list[int] = []
    for line in sys.stdin:
        matches = get_matches(line)
        first = LOOKUP.get(matches[0], matches[0])
        last = LOOKUP.get(matches[-1], matches[-1])
        number = int(f"{first}{last}")
        numbers.append(number)
        LOG.info(
            (line, matches, (first, last), number),
            single=len(matches) == 1,
            equal=(first == last),
        )
    LOG.info("total", total=sum(numbers))
    assert get_matches("oneight") == ["one", "eight"], get_matches("oneight")


if __name__ == "__main__":
    main()
