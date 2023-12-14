import itertools
import json
import sys
import time
import typing
from pathlib import Path

import parsy
import structlog
import tqdm
import typer
from numba import njit, types, jit
from numba.typed import Dict

app = typer.Typer()
LOG = structlog.get_logger()


class Node(typing.TypedDict):
    name: str
    L: str
    R: str


class RawMap(typing.TypedDict):
    steps: list[str]
    nodes: list[Node]


class Map(typing.TypedDict):
    steps: list[str]
    nodes: dict[str, Node]


EXAMPLE = """RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
"""

STEPS = parsy.char_from("LR").at_least(1)
NODE = parsy.seq(
    name=parsy.regex(r"[0-9A-Z]{,3}") << parsy.string(" = ("),
    L=parsy.regex(r"[0-9A-Z]{,3}") << parsy.string(", "),
    R=parsy.regex(r"[0-9A-Z]{,3}") << parsy.string(")"),
)
GRAPH_FILE = parsy.seq(
    steps=STEPS << parsy.string("\n\n"),
    nodes=NODE.sep_by(parsy.string("\n")),
)


def parse(input: str) -> Map:
    raw_map: RawMap = GRAPH_FILE.parse(input.strip())
    map: Map = {
        "steps": raw_map["steps"],
        "nodes": {node["name"]: node for node in raw_map["nodes"]},
    }
    return map


assert parse(EXAMPLE) == {
    "steps": ["R", "L"],
    "nodes": {
        "AAA": {"name": "AAA", "L": "BBB", "R": "CCC"},
        "BBB": {"name": "BBB", "L": "DDD", "R": "EEE"},
        "CCC": {"name": "CCC", "L": "ZZZ", "R": "GGG"},
        "DDD": {"name": "DDD", "L": "DDD", "R": "DDD"},
        "EEE": {"name": "EEE", "L": "EEE", "R": "EEE"},
        "GGG": {"name": "GGG", "L": "GGG", "R": "GGG"},
        "ZZZ": {"name": "ZZZ", "L": "ZZZ", "R": "ZZZ"},
    },
}, parse(EXAMPLE)


@app.command()
def parse_to_json(input: Path):
    json.dump(parse(input.open("r").read()), sys.stdout)


@jit
def solution(graph: dict):
    steps = itertools.cycle(graph["steps"])
    nodes = graph["nodes"]
    current_nodes = [node for node in nodes.values() if node["name"].endswith("A")]
    desired_z_count = len(current_nodes)
    # LOG.info("Starting nodes", nodes=current_nodes)
    # steps_enumerator = enumerate(tqdm.tqdm(steps))
    steps_enumerator = enumerate(steps)
    i = 0
    z_count = 0
    start_time = time.monotonic()
    while z_count != desired_z_count:
        i, step = next(steps_enumerator)

        next_nodes = []
        z_count = 0
        for node in current_nodes:
            next_nodes.append(nodes[node[step]])
            if node["name"][2] == "Z":
                z_count += 1
        if i % 1_000_000 == 0:
            now = time.monotonic()
            duration = start_time - now
            start_time = now
            print(
                dict(
                    count=i + 1,
                    step=step,
                    current_nodes=[node["name"] for node in current_nodes],
                    next_nodes=[node["name"] for node in next_nodes],
                    z_count=z_count,
                    duration=duration,
                )
            )
        #     # if i > 1:
        #     #     return
        current_nodes = next_nodes
    print(f"total={i + 1}")


@app.command()
def solve(input: Path):
    graph = parse(input.open("r").read())
    solution(graph)


if __name__ == "__main__":
    app()
