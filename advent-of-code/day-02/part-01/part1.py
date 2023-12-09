import sys

import parsy
import structlog

LOG = structlog.get_logger()


def main():
    for line in sys.stdin:
        print(line)


if __name__ == "__main__":
    main()
