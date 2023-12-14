from collections import Counter
from pathlib import Path

import typer

app = typer.Typer()

CARD_TO_RANK_MAPPING = {
    "J": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "T": 9,
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
        if "J" in cards:
            joker_count = counter.pop("J")
            # most_common(1) -> [("K", 1)]
            if joker_count == 5:
                counter["A"] = 5
            else:
                if counter[counter.most_common(1)[0][0]] == 3:
                    print(counter)
                counter[counter.most_common(1)[0][0]] += joker_count
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
