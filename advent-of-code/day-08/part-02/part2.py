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

from numba import njit

app = typer.Typer()
LOG = structlog.get_logger()


class Node(typing.TypedDict):
    name: str
    L: str
    R: str
    A: bool
    Z: bool


class IntNode(typing.TypedDict):
    name: int
    L: int
    R: int
    A: bool
    Z: bool


class RawMap(typing.TypedDict):
    steps: list[str]
    nodes: list[Node]


class IntMap(typing.TypedDict):
    steps: list[int]
    nodes: list[IntNode]
    name_mapping: dict[str, int]


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
        int_map: IntMap = {"name_mapping": {}, "nodes": [], "steps": []}
        int_map["steps"] = [0 if s == "L" else 1 for s in parsed["steps"]]
        names: dict[str, int] = {}
        for i, name in enumerate(parsed["nodes"].keys()):
            names[name] = i
        for node in parsed["nodes"].values():
            int_node: IntNode = {
                "A": node["A"],
                "Z": node["Z"],
                "L": names[node["L"]],
                "R": names[node["R"]],
                "name": names[node["name"]],
            }
            int_map["nodes"].append(int_node)
        int_map["nodes"] = list(sorted(int_map["nodes"], key=lambda n: n["name"]))
        int_map["name_mapping"] = names
    json.dump(parsed, sys.stdout)


@app.command()
def graph(input: Path):
    graph = parse(input.open("r").read())
    sys.stdout.write("digraph {\n")
    for name, node in graph["nodes"].items():
        for branch in ["L", "R"]:
            sys.stdout.write(f"N_{name} -> N_{node[branch]};\n")
    sys.stdout.write("}\n")


@app.command()
def graph_steps(input: Path, output: Path):
    fp = output.open("w")
    graph = parse(input.open("r").read())
    fp.write("digraph {\n")
    a_nodes = [n for n in graph["nodes"].values() if n["name"].endswith("A")]
    # current_nodes = {i: n for i, n in enumerate(a_nodes)}
    current_nodes = {n["name"]: n for n in a_nodes}
    for step_count, step in enumerate(itertools.cycle(graph["steps"])):
        if not current_nodes:
            break
        for i, current_node in list(current_nodes.items()):
            next_node = graph["nodes"][current_node[step]]
            fp.write(f"N_{i}_{current_node['name']} -> N_{i}_{next_node['name']};\n")
            if next_node["name"][-1] == "Z":
                LOG.info(
                    "finished node", i=i, node=next_node, step_count=step_count + 1
                )
                del current_nodes[i]
            else:
                current_nodes[i] = next_node

    fp.write("}\n")


@njit
def njit_divisible():
    numbers = [12599, 17873, 19631, 20803, 21389, 23147]
    largest = max(numbers)
    numbers.remove(largest)
    i = 1
    while True:
        steps = largest * i
        divisible = True
        if i % 1_000_000 == 0:
            print(("step", i, steps))
        for number in numbers:
            if steps % number != 0:
                divisible = False
        if divisible:
            print(("divisible after", steps))
            return
        i += 1


@app.command()
def find_divisible_number():
    """Find multiple of largest number which is divisible by others"""
    njit_divisible()
    return
    numbers = [12599, 17873, 19631, 20803, 21389, 23147]
    largest = max(numbers)
    numbers.remove(largest)
    i = 1
    while True:
        steps = largest * i
        divisible = True
        if i % 100_000 == 0:
            LOG.info("step", i=i, steps=steps)
        for number in numbers:
            if steps % number != 0:
                divisible = False
        if divisible:
            LOG.info("divisible after", steps=steps)
        i += 1


# TODO: look at how long each graph takes to loop, how long until (step[i], current_node) repeats
@app.command()
def does_graph_loop(input: Path):
    graph = parse(input.open("r").read())
    a_nodes = [n for n in graph["nodes"].values() if n["name"].endswith("A")]
    # current_nodes = {i: n for i, n in enumerate(a_nodes)}
    current_nodes = {n["name"]: n for n in a_nodes}
    seen_steps: set[tuple[int, int, str]] = set()
    steps = list(enumerate(graph["steps"]))
    # LOG.info("steps", steps=steps)
    for step_count, (step_index, step) in enumerate(itertools.cycle(steps)):
        if step_count % 100_000 == 0 and step_count > 1:
            LOG.info(
                "step",
                step_count=step_count,
                step=step,
                current_nodes=current_nodes,
                seen_steps=len(seen_steps),
            )
        if not current_nodes:
            break
        for i, current_node in list(current_nodes.items()):
            step_info = (i, step_index, current_node["name"])
            if step_info in seen_steps:
                LOG.info(
                    "node steps repeated",
                    i=i,
                    node=current_node,
                    step_count=step_count + 1,
                )
                del current_nodes[i]
            else:
                current_nodes[i] = graph["nodes"][current_node[step]]
                seen_steps.add(step_info)


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
