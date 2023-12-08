import re
import sys

import structlog

LOG = structlog.get_logger()


def main():
    numbers: list[int] = []
    for line in sys.stdin:
        matches = re.findall(r"[0-9]", line)
        first = matches[0]
        last = matches[-1]
        number = int(f"{first}{last}")
        numbers.append(number)
        LOG.info((line, matches, number))
    LOG.info("total", total=sum(numbers))


if __name__ == "__main__":
    main()
