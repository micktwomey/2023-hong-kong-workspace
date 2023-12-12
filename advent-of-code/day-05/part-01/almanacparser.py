"""Parses alamanacs

"""

import typing

import parsy

EXAMPLE = """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4

"""


class MappingTable(typing.TypedDict):
    source: int
    destination: int
    count: int


class Mapping(typing.TypedDict):
    source: str
    destination: str
    mappings: list[MappingTable]


class Almanac(typing.TypedDict):
    seeds: list[int]
    next_mapping: dict[str, str]
    mappings: list[Mapping]


SEEDS = (
    parsy.string("seeds:")
    >> parsy.whitespace
    >> parsy.regex(r"[0-9]+").map(int).sep_by(parsy.string(" "))
)

MAPPING_LINE = parsy.seq(
    destination=parsy.regex(r"[0-9]+").map(int) << parsy.whitespace,
    source=parsy.regex(r"[0-9]+").map(int) << parsy.whitespace,
    count=parsy.regex(r"[0-9]+").map(int),
)

MAPPING = parsy.seq(
    source=parsy.regex(r"[a-z]+") << parsy.string("-to-"),
    destination=parsy.regex(r"[a-z]+") << parsy.string(" map:\n"),
    mappings=MAPPING_LINE.sep_by(parsy.string("\n")),
)


ALMANAC = parsy.seq(
    seeds=SEEDS << parsy.string("\n\n"), mappings=MAPPING.sep_by(parsy.string("\n\n"))
)


def parse(input: str) -> Almanac:
    almanac: Almanac = ALMANAC.parse(input.strip())
    almanac["next_mapping"] = {}
    for mapping in almanac["mappings"]:
        almanac["next_mapping"][mapping["source"]] = mapping["destination"]

    return almanac


assert parse(EXAMPLE) == {
    "seeds": [79, 14, 55, 13],
    "mappings": [
        {
            "source": "seed",
            "destination": "soil",
            "mappings": [
                {"destination": 50, "source": 98, "count": 2},
                {"destination": 52, "source": 50, "count": 48},
            ],
        },
        {
            "source": "soil",
            "destination": "fertilizer",
            "mappings": [
                {"destination": 0, "source": 15, "count": 37},
                {"destination": 37, "source": 52, "count": 2},
                {"destination": 39, "source": 0, "count": 15},
            ],
        },
        {
            "source": "fertilizer",
            "destination": "water",
            "mappings": [
                {"destination": 49, "source": 53, "count": 8},
                {"destination": 0, "source": 11, "count": 42},
                {"destination": 42, "source": 0, "count": 7},
                {"destination": 57, "source": 7, "count": 4},
            ],
        },
        {
            "source": "water",
            "destination": "light",
            "mappings": [
                {"destination": 88, "source": 18, "count": 7},
                {"destination": 18, "source": 25, "count": 70},
            ],
        },
        {
            "source": "light",
            "destination": "temperature",
            "mappings": [
                {"destination": 45, "source": 77, "count": 23},
                {"destination": 81, "source": 45, "count": 19},
                {"destination": 68, "source": 64, "count": 13},
            ],
        },
        {
            "source": "temperature",
            "destination": "humidity",
            "mappings": [
                {"destination": 0, "source": 69, "count": 1},
                {"destination": 1, "source": 0, "count": 69},
            ],
        },
        {
            "source": "humidity",
            "destination": "location",
            "mappings": [
                {"destination": 60, "source": 56, "count": 37},
                {"destination": 56, "source": 93, "count": 4},
            ],
        },
    ],
    "next_mapping": {
        "seed": "soil",
        "soil": "fertilizer",
        "fertilizer": "water",
        "water": "light",
        "light": "temperature",
        "temperature": "humidity",
        "humidity": "location",
    },
}, parse(EXAMPLE)

if __name__ == "__main__":
    import sys

    print(parse(sys.stdin.read()))
