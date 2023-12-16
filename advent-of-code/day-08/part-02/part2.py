from pathlib import Path
import json
import itertools
import sys
import typing
import time

import structlog
import typer
import parsy
import tqdm

app = typer.Typer()
LOG = structlog.get_logger()


class Node(typing.TypedDict):
    name: str
    L: str
    R: str
    A: bool
    Z: bool


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
    for node in map["nodes"].values():
        node["A"] = node["name"].endswith("A")
        node["Z"] = node["name"].endswith("Z")
    return map


assert parse(EXAMPLE) == {
    "steps": ["R", "L"],
    "nodes": {
        "AAA": {"name": "AAA", "L": "BBB", "R": "CCC", "A": True, "Z": False},
        "BBB": {"name": "BBB", "L": "DDD", "R": "EEE", "A": False, "Z": False},
        "CCC": {"name": "CCC", "L": "ZZZ", "R": "GGG", "A": False, "Z": False},
        "DDD": {"name": "DDD", "L": "DDD", "R": "DDD", "A": False, "Z": False},
        "EEE": {"name": "EEE", "L": "EEE", "R": "EEE", "A": False, "Z": False},
        "GGG": {"name": "GGG", "L": "GGG", "R": "GGG", "A": False, "Z": False},
        "ZZZ": {"name": "ZZZ", "L": "ZZZ", "R": "ZZZ", "A": False, "Z": True},
    },
}, parse(EXAMPLE)


@app.command()
def parse_to_json(input: Path, use_ints: bool = False):
    parsed = parse(input.open("r").read())
    if use_ints:
        parsed["steps"] = [0 if s == "L" else 1 for s in parsed["steps"]]
        names: dict[str, int] = {}
        for i, name in enumerate(parsed["nodes"].keys()):
            names[name] = i
        for node in parsed["nodes"].values():
            name = node["name"]
            node["name"] = names[name]
            # node[0] = node["L"]
            # node[1] = node["R"]
            # del node["L"]
            # del node["R"]
            for branch in ["L", "R"]:
                node[branch] = names[node[branch]]
        parsed["nodes"] = [
            v for v in sorted(parsed["nodes"].values(), key=lambda n: n["name"])
        ]
        parsed["name_mapping"] = names
    json.dump(parsed, sys.stdout)


@app.command()
def solve(input: Path):
    graph = parse(input.open("r").read())
    steps = itertools.cycle(graph["steps"])
    nodes = graph["nodes"]
    current_nodes = [node for node in nodes.values() if node["name"].endswith("A")]
    desired_z_count = len(current_nodes)
    LOG.info("Starting nodes", nodes=current_nodes)
    steps_enumerator = enumerate(tqdm.tqdm(steps))
    # steps_enumerator = enumerate(steps)
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
        if z_count > 2:
            print(z_count)
        # if i % 1_000_000 == 0:
        #     now = time.monotonic()
        #     duration = start_time - now
        #     start_time = now
        #     LOG.info(
        #         "step",
        #         count=i + 1,
        #         step=step,
        #         current_nodes=[node["name"] for node in current_nodes],
        #         next_nodes=[node["name"] for node in next_nodes],
        #         z_count=z_count,
        #         duration=duration,
        #     )
        #     # if i > 1:
        #     #     return
        current_nodes = next_nodes
    LOG.info("total", steps=i + 1)


if __name__ == "__main__":
    app()
