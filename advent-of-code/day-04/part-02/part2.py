import functools
from pathlib import Path

import cardparser
import structlog
import typer

APP = typer.Typer()
LOG = structlog.get_logger()


class Cards:
    def __init__(self, cards: list[cardparser.Card]):
        self.cards: dict[int, cardparser.Card] = {card["card"]: card for card in cards}

    @functools.cache
    def calculate_copies_won(self, card_number: int) -> int:
        card: cardparser.Card = self.cards[card_number]
        winners = card["winning_numbers"].intersection(card["numbers"])
        won = len(winners)
        for i in range(card_number + 1, card_number + 1 + len(winners)):
            won += self.calculate_copies_won(i)
        return won


@APP.command()
def main(
    input: Path,
    expected: int = -1,
):
    parsed = cardparser.parse(input.open("r").read())
    LOG.debug("parsed", parsed=parsed)

    cards = Cards(parsed)
    total = 0
    for card_number, card in cards.cards.items():
        won_cards = cards.calculate_copies_won(card_number)
        LOG.info("card", card=card, card_number=card_number, won_cards=won_cards)
        total += won_cards + 1
    LOG.info("total", total=total)
    if expected > 0 and total != expected:
        LOG.warning("wrong expected total", expected=expected, total=total)


if __name__ == "__main__":
    APP()
