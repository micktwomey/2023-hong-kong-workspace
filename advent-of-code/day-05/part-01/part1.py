import functools
from pathlib import Path

import almanacparser
import structlog
import typer

APP = typer.Typer()
LOG = structlog.get_logger()


class Almanac:
    def __init__(self, almanac: almanacparser.Almanac):
        self.almanac = almanac
        self.mappings: dict[str, list[almanacparser.MappingTable]] = {}
        # self.destination_lookup: dict[str, dict[int, int]] = {}
        for mapping in self.almanac["mappings"]:
            self.mappings[mapping["destination"]] = mapping["mappings"]
        #     self.destination_lookup.setdefault(mapping["destination"], {})
        #     destination_name = mapping["destination"]
        #     for mapping_table in mapping["mappings"]:
        #         count = mapping_table["count"]
        #         source_number = mapping_table["source"]
        #         destination_number = mapping_table["destination"]
        #         for i in range(count):
        #             assert (
        #                 source_number + i
        #                 not in self.destination_lookup[destination_name]
        #             )
        #             # LOG.info(
        #             #     "add-mapping",
        #             #     destination_name=destination_name,
        #             #     source=source_number + i,
        #             #     destination=destination_number + i,
        #             # )
        #             self.destination_lookup[destination_name][source_number + i] = (
        #                 destination_number + i
        #             )

    def lookup_next(self, destination_name: str, source_value: int) -> int:
        for mapping in self.mappings[destination_name]:
            if source_value >= mapping["source"] and source_value < (
                mapping["source"] + mapping["count"]
            ):
                return mapping["destination"] + (source_value - mapping["source"])
        return source_value

    def iterate_lookups(self, start: str):
        current = start
        while True:
            try:
                next = self.almanac["next_mapping"][current]
            except KeyError:
                return
            yield next
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
    for seed in almanac.almanac["seeds"]:
        LOG.info("seed", seed=seed)
        current_result = seed
        previous_mapping = "seed"
        for next_mapping in almanac.iterate_lookups("seed"):
            LOG.info(
                "lookup",
                mapping=next_mapping,
                key=current_result,
            )
            current_result = almanac.lookup_next(next_mapping, current_result)
            LOG.info(
                "result",
                seed=seed,
                next_mapping=next_mapping,
                previous_mapping=previous_mapping,
                current_result=current_result,
            )
            previous_mapping = next_mapping

        locations.append(current_result)
        LOG.info("seed", seed=seed, location=current_result)

    location = min(locations)
    LOG.info("location", location=location)
    if expected > 0 and location != expected:
        LOG.warning("wrong expected location", expected=expected, location=location)


if __name__ == "__main__":
    APP()
