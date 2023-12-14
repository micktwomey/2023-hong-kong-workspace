from pathlib import Path
import json
import itertools
import sys
import typing

import structlog
import typer
import parsy

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
    name=parsy.regex(r"[A-Z]{,3}") << parsy.string(" = ("),
    L=parsy.regex(r"[A-Z]{,3}") << parsy.string(", "),
    R=parsy.regex(r"[A-Z]{,3}") << parsy.string(")"),
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


@app.command()
def solve(input: Path):
    graph = parse(input.open("r").read())
    steps = itertools.cycle(graph["steps"])
    nodes = graph["nodes"]
    current_node = nodes["AAA"]
    steps_enumerator = enumerate(steps)
    i = 0
    while current_node["name"] != "ZZZ":
        i, step = next(steps_enumerator)
        count = i + 1
        next_node_name = current_node[step]
        next_node = nodes[next_node_name]
        LOG.info(
            "step",
            count=count,
            step=step,
            current_node=current_node,
            next_node_name=next_node_name,
            next_node=next_node,
        )
        current_node = next_node
    LOG.info("total", steps=i + 1)


if __name__ == "__main__":
    app()
