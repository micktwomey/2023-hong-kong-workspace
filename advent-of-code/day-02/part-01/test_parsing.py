import gameparser


def test_parser():
    assert gameparser.GAME.parse("Game 1") == 1
    assert gameparser.DRAW.parse("3 blue") == {
        "count": 3,
        "colour": gameparser.Colour.blue,
    }
    assert gameparser.REVEAL.parse("3 blue, 4 red") == [
        {
            "count": 3,
            "colour": gameparser.Colour.blue,
        },
        {
            "count": 4,
            "colour": gameparser.Colour.red,
        },
    ]

    assert gameparser.REVEALS.parse("3 blue, 4 red; 2 green, 2 red, 1 blue") == [
        [
            {
                "count": 3,
                "colour": gameparser.Colour.blue,
            },
            {
                "count": 4,
                "colour": gameparser.Colour.red,
            },
        ],
        [
            {
                "count": 2,
                "colour": gameparser.Colour.green,
            },
            {
                "count": 2,
                "colour": gameparser.Colour.red,
            },
            {
                "count": 1,
                "colour": gameparser.Colour.blue,
            },
        ],
    ]

    assert gameparser.GAME_ROUND.parse(
        "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"
    ) == {
        "game": 1,
        "reveals": [
            [
                {
                    "count": 3,
                    "colour": gameparser.Colour.blue,
                },
                {
                    "count": 4,
                    "colour": gameparser.Colour.red,
                },
            ],
            [
                {
                    "count": 1,
                    "colour": gameparser.Colour.red,
                },
                {
                    "count": 2,
                    "colour": gameparser.Colour.green,
                },
                {
                    "count": 6,
                    "colour": gameparser.Colour.blue,
                },
            ],
            [
                {
                    "count": 2,
                    "colour": gameparser.Colour.green,
                }
            ],
        ],
    }


def test_parse_full_game():
    assert gameparser.parse("Game 1: 1 red; 2 green\nGame 2: 2 red") == [
        {
            "game": 1,
            "reveals": [
                [
                    {
                        "count": 1,
                        "colour": gameparser.Colour.red,
                    }
                ],
                [
                    {
                        "count": 2,
                        "colour": gameparser.Colour.green,
                    }
                ],
            ],
        },
        {
            "game": 2,
            "reveals": [
                [
                    {
                        "count": 2,
                        "colour": gameparser.Colour.red,
                    }
                ]
            ],
        },
    ]
