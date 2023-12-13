import functools
from pathlib import Path

# from numba import jit
import almanacparser
import structlog
import tqdm
import typer

APP = typer.Typer()
LOG = structlog.get_logger()


class Almanac:
    def __init__(self, almanac: almanacparser.Almanac):
        self.almanac = almanac
        self.mapping_tables: dict[str, list[almanacparser.MappingTable]] = {}
        self.mappings: dict[str, almanacparser.Mapping] = {}
        # self.destination_lookup: dict[str, dict[int, int]] = {}
        for mapping in self.almanac["mappings"]:
            mapping_tables = mapping["mappings"]
            destination = mapping["destination"]
            self.mapping_tables[destination] = mapping_tables
            self.mappings[destination] = mapping
            # for m in mappings:
            #     m["min"] = min(mv["source"] for mv in m)

    # @functools.cache
    def lookup_next(self, destination_name: str, source_value: int) -> int:
        if (
            source_value >= self.mappings[destination_name]["min_source"]
            and source_value < self.mappings[destination_name]["max_source"]
        ):
            for mapping in self.mapping_tables[destination_name]:
                if (
                    source_value >= mapping["min_source"]
                    and source_value < mapping["max_source"]
                ):
                    return mapping["destination"] + (source_value - mapping["source"])
        return source_value

    @functools.cache
    def iterate_lookups(self, start: str) -> list[str]:
        current = start
        result = []
        while True:
            try:
                next = self.almanac["next_mapping"][current]
            except KeyError:
                return result
            result.append(next)
            current = next


@APP.command()
def main(
    input: Path,
    expected: int = -1,
):
    parsed = almanacparser.parse(input.open("r").read())
    LOG.debug("parsed", parsed=parsed)

    almanac = Almanac(parsed)
    LOG.debug(
        "almanac",
        lookups=list(almanac.iterate_lookups("seed")),
    )

    locations: list[int] = []
    for seed_range in tqdm.tqdm(almanac.almanac["seeds"], desc="Seed Ranges"):
        seeds = (seed_range["start"] + i for i in range(seed_range["end"]))
        total = seed_range["start"] + (seed_range["end"] - 1)
        for i, seed in enumerate(tqdm.tqdm(seeds, desc="Seeds", total=total)):
            if i >= 1e6:
                return
            # LOG.info("seed", seed=seed)
            current_result: int = seed
            # previous_mapping = "seed"
            next_mapping: str
            for next_mapping in almanac.iterate_lookups("seed"):
                # LOG.info(
                #     "lookup",
                #     mapping=next_mapping,
                #     key=current_result,
                # )
                # pass
                current_result = almanac.lookup_next(next_mapping, current_result)
                # LOG.info(
                #     "result",
                #     seed=seed,
                #     next_mapping=next_mapping,
                #     previous_mapping=previous_mapping,
                #     current_result=current_result,
                # )
                # previous_mapping = next_mapping

            locations.append(current_result)
            # LOG.info("seed", seed=seed, location=current_result)

    location = min(locations)
    LOG.info("location", location=location)
    if expected > 0 and location != expected:
        LOG.warning("wrong expected location", expected=expected, location=location)


if __name__ == "__main__":
    APP()
