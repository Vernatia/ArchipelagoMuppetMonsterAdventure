from enum import StrEnum


class Ability(StrEnum):
    CLIMB = "climb"
    SWIM = "swim"
    GLIDE = "glide"
    PUSH = "push"
    SMASH = "smash"
    # TODO: implement these (if possible)
    GLOVE = "glove"
    SPIN = "spin"


class MMALocationData:
    ability_requirements: list[Ability] | None

    def __init__(self, name: str, ability_requirements: list[Ability] | None = None):
        self.name: str = name
        self.ability_requirements = ability_requirements


class MMARegion:
    def __init__(self, name: str, locations: list[MMALocationData]) -> None:
        self.name: str = name
        self.locations: list[MMALocationData] = locations
        pass


# TODO: other regions
all_locations_table: list[MMARegion] = [
    MMARegion(
        "Peacock Purgatory",
        [
            MMALocationData("Wocka Wocka Werebear Amulet - By tutorial flags"),
            MMALocationData("Wocka Wocka Werebear Amulet - On stairs near gardener"),
            MMALocationData("Wocka Wocka Werebear Amulet - On hill by lake"),
            MMALocationData("Wocka Wocka Werebear Amulet - By climbable wall"),
            MMALocationData("Muck Monster Amulet - By the lake"),
            MMALocationData("Muck Monster Amulet - Up climbable wall by Werebear Amulet", [Ability.CLIMB]),
            MMALocationData("Muck Monster Amulet - On path before climable wall"),
            MMALocationData("Muck Monster Amulet - Up climable wall by Muck Monster Amulet", [Ability.CLIMB]),
            MMALocationData("Noseferatu Amulet - Bottom of the lake", [Ability.SWIM]),
            MMALocationData("Noseferatu Amulet - By sundial"),
            MMALocationData("Noseferatu Amulet - Up super-jump platform"),
            MMALocationData("Noseferatu Amulet - Up stairs after triggering switch", [Ability.GLOVE]),
        ],
    ),
]


def location_name_to_id(base_id: int) -> dict[str, int]:
    """Converts all locations from their `[Region: [Name: Data]]` format into `[Name: ID]`,
    where `ID` is a deterministic value greater than `base_id`."""
    result: dict[str, int] = {}
    for group_idx, region_data in enumerate(all_locations_table):
        for item_idx, location in enumerate(region_data.locations):
            result.update({location.name: base_id + group_idx + item_idx})
    return result


def location_name_groups() -> dict[str, set[str]]:
    """Converts all locations from their `[Region: [Name: Data]]` format into `[Region: [Name]]`."""
    result: dict[str, set[str]] = {}
    for region_data in all_locations_table:
        result[region_data.name] = {x.name for x in region_data.locations}
    return result
