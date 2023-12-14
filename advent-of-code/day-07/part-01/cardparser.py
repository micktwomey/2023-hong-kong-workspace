from collections import Counter
import json
from pathlib import Path

import typer

app = typer.Typer()

CARD_TO_RANK_MAPPING = {
    "2": 0,
    "3": 1,
    "4": 2,
    "5": 3,
    "6": 4,
    "7": 5,
    "8": 6,
    "9": 7,
    "T": 8,
    "J": 9,
    "Q": 10,
    "K": 11,
    "A": 12,
}


@app.command()
def main(input: Path):
    all_cards = []
    for line in (line.strip() for line in input.open("r")):
        cards, score = line.split(" ")
        score = int(score)
        counter = Counter(cards)
        hand = list(sorted(counter.values(), reverse=True))
        card_rank = [CARD_TO_RANK_MAPPING[card] for card in cards]
        all_cards.append((hand, card_rank, cards, score))
    all_cards.sort()
    total = 0
    for i, row in enumerate(all_cards):
        score = (i + 1) * row[-1]
        print((i, row, score))
        total += score
    print(f"total: {total}")


if __name__ == "__main__":
    app()
