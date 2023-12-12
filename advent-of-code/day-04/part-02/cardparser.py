"""Parses cards

"""

import typing

import parsy

EXAMPLE = """Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
"""


class Card(typing.TypedDict):
    card: int
    winning_numbers: set[int]
    numbers: set[int]


CARD = parsy.string("Card") >> parsy.whitespace >> parsy.regex(r"[0-9]+").map(int)

NUMBERS = (
    parsy.regex(r"[0-9]+").map(int).sep_by(parsy.whitespace.at_least(n=1)).map(set)
)

ROW = parsy.seq(
    card=CARD << parsy.string(":") << parsy.whitespace,
    winning_numbers=(
        NUMBERS << parsy.whitespace << parsy.string("|") << parsy.whitespace
    ),
    numbers=NUMBERS,
)

ALL_CARDS = ROW.sep_by(parsy.string("\n"))


def parse(input: str) -> list[Card]:
    return ALL_CARDS.parse(input.strip())


assert parse(EXAMPLE) == [
    {
        "card": 1,
        "winning_numbers": {41, 48, 83, 86, 17},
        "numbers": {83, 86, 6, 31, 17, 9, 48, 53},
    },
    {
        "card": 2,
        "winning_numbers": {13, 32, 20, 16, 61},
        "numbers": {61, 30, 68, 82, 17, 32, 24, 19},
    },
    {
        "card": 3,
        "winning_numbers": {1, 21, 53, 59, 44},
        "numbers": {69, 82, 63, 72, 16, 21, 14, 1},
    },
    {
        "card": 4,
        "winning_numbers": {41, 92, 73, 84, 69},
        "numbers": {59, 84, 76, 51, 58, 5, 54, 83},
    },
    {
        "card": 5,
        "winning_numbers": {87, 83, 26, 28, 32},
        "numbers": {88, 30, 70, 12, 93, 22, 82, 36},
    },
    {
        "card": 6,
        "winning_numbers": {31, 18, 13, 56, 72},
        "numbers": {74, 77, 10, 23, 35, 67, 36, 11},
    },
]

if __name__ == "__main__":
    import sys

    print(parse(sys.stdin.read()))
