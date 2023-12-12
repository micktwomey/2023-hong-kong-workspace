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
    min_source: int
    max_source: int


class Mapping(typing.TypedDict):
    source: str
    destination: str
    mappings: list[MappingTable]
    min_source: int
    max_source: int


class Seed(typing.TypedDict):
    start: int
    end: int


class Almanac(typing.TypedDict):
    seeds: list[Seed]
    next_mapping: dict[str, str]
    mappings: list[Mapping]


SEEDS = (
    parsy.string("seeds:")
    >> parsy.whitespace
    >> parsy.seq(
        start=parsy.regex(r"[0-9]+").map(int) << parsy.whitespace,
        end=parsy.regex(r"[0-9]+").map(int),
    ).sep_by(parsy.string(" "))
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
        max_source: int | None = None
        min_source: int | None = None
        for mapping_table in mapping["mappings"]:
            source = mapping_table["source"]
            if min_source is None:
                min_source = source

            mt_max_source = source + (mapping_table["count"] - 1)
            if max_source is None:
                max_source = mt_max_source
            mapping_table["min_source"] = source
            mapping_table["max_source"] = mt_max_source
            min_source = min(source, min_source)
            max_source = max(max_source, mt_max_source)
        assert min_source is not None
        mapping["min_source"] = min_source
        assert max_source is not None
        mapping["max_source"] = max_source

    return almanac


assert parse(EXAMPLE) == {
    "seeds": [{"start": 79, "end": 14}, {"start": 55, "end": 13}],
    "mappings": [
        {
            "source": "seed",
            "destination": "soil",
            "mappings": [
                {
                    "destination": 50,
                    "source": 98,
                    "count": 2,
                    "min_source": 98,
                    "max_source": 99,
                },
                {
                    "destination": 52,
                    "source": 50,
                    "count": 48,
                    "min_source": 50,
                    "max_source": 97,
                },
            ],
            "min_source": 50,
            "max_source": 99,
        },
        {
            "source": "soil",
            "destination": "fertilizer",
            "mappings": [
                {
                    "destination": 0,
                    "source": 15,
                    "count": 37,
                    "min_source": 15,
                    "max_source": 51,
                },
                {
                    "destination": 37,
                    "source": 52,
                    "count": 2,
                    "min_source": 52,
                    "max_source": 53,
                },
                {
                    "destination": 39,
                    "source": 0,
                    "count": 15,
                    "min_source": 0,
                    "max_source": 14,
                },
            ],
            "min_source": 0,
            "max_source": 53,
        },
        {
            "source": "fertilizer",
            "destination": "water",
            "mappings": [
                {
                    "destination": 49,
                    "source": 53,
                    "count": 8,
                    "min_source": 53,
                    "max_source": 60,
                },
                {
                    "destination": 0,
                    "source": 11,
                    "count": 42,
                    "min_source": 11,
                    "max_source": 52,
                },
                {
                    "destination": 42,
                    "source": 0,
                    "count": 7,
                    "min_source": 0,
                    "max_source": 6,
                },
                {
                    "destination": 57,
                    "source": 7,
                    "count": 4,
                    "min_source": 7,
                    "max_source": 10,
                },
            ],
            "min_source": 0,
            "max_source": 60,
        },
        {
            "source": "water",
            "destination": "light",
            "mappings": [
                {
                    "destination": 88,
                    "source": 18,
                    "count": 7,
                    "min_source": 18,
                    "max_source": 24,
                },
                {
                    "destination": 18,
                    "source": 25,
                    "count": 70,
                    "min_source": 25,
                    "max_source": 94,
                },
            ],
            "min_source": 18,
            "max_source": 94,
        },
        {
            "source": "light",
            "destination": "temperature",
            "mappings": [
                {
                    "destination": 45,
                    "source": 77,
                    "count": 23,
                    "min_source": 77,
                    "max_source": 99,
                },
                {
                    "destination": 81,
                    "source": 45,
                    "count": 19,
                    "min_source": 45,
                    "max_source": 63,
                },
                {
                    "destination": 68,
                    "source": 64,
                    "count": 13,
                    "min_source": 64,
                    "max_source": 76,
                },
            ],
            "min_source": 45,
            "max_source": 99,
        },
        {
            "source": "temperature",
            "destination": "humidity",
            "mappings": [
                {
                    "destination": 0,
                    "source": 69,
                    "count": 1,
                    "min_source": 69,
                    "max_source": 69,
                },
                {
                    "destination": 1,
                    "source": 0,
                    "count": 69,
                    "min_source": 0,
                    "max_source": 68,
                },
            ],
            "min_source": 0,
            "max_source": 69,
        },
        {
            "source": "humidity",
            "destination": "location",
            "mappings": [
                {
                    "destination": 60,
                    "source": 56,
                    "count": 37,
                    "min_source": 56,
                    "max_source": 92,
                },
                {
                    "destination": 56,
                    "source": 93,
                    "count": 4,
                    "min_source": 93,
                    "max_source": 96,
                },
            ],
            "min_source": 56,
            "max_source": 96,
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
    import json

    json.dump(parse(sys.stdin.read()), sys.stdout)
