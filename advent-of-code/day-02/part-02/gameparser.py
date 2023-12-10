"""Parses games

Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green


"""

import enum
import typing

import parsy


class Colour(enum.StrEnum):
    red = "red"
    green = "green"
    blue = "blue"


class Reveal(typing.TypedDict):
    count: int
    colour: Colour


class GameRound(typing.TypedDict):
    game: int
    reveals: list[list[Reveal]]


GAME = parsy.string("Game") >> parsy.whitespace >> parsy.regex(r"[0-9]+").map(int)

DRAW = parsy.seq(
    count=parsy.regex(r"[0-9]+").map(int) << parsy.whitespace,
    colour=parsy.from_enum(Colour),
)

REVEAL = DRAW.sep_by(parsy.string(", "))

REVEALS = REVEAL.sep_by(parsy.string("; "))

GAME_ROUND = parsy.seq(game=GAME << parsy.string(": "), reveals=REVEALS)
FULL_GAME = GAME_ROUND.sep_by(parsy.string("\n"))


def parse(input: str) -> list[GameRound]:
    return FULL_GAME.parse(input.strip())
