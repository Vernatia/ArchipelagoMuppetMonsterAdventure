from enum import Flag, auto


class AbilityFlag(Flag):
    CLIMB = auto()
    SWIM = auto()
    GLIDE = auto()
    PUSH = auto()
    SMASH = auto()
    # TODO: implement these (if possible)
    GLOVE = auto()
    SPIN = auto()


class MMALocationData:
    ability_requirements: list[AbilityFlag] | None

    def __init__(self, name: str, ability_requirements: list[AbilityFlag] | None = None):
        self.name: str = name
        # Each flag lists the unique combination of abilities which unlocks this location.
        # Alternatives should be provided as a separate entry.
        # e.g. The location can be unlocked by either "climb and swim" OR "climb and glide".
        # This would be represented as: [AbilityFlag.CLIMB | AbilityFlag.SWIM, AbilityFlag.CLIMB | AbilityFlag.GLIDE]
        self.ability_requirements = ability_requirements


class MMARegion:
    def __init__(self, name: str, identifier: str, state_address: int | None, locations: list[MMALocationData]) -> None:
        self.name: str = name
        self.identifier: str = identifier
        self.state_address: int | None = state_address
        self.locations: list[MMALocationData] = locations
        pass


# TODO: other regions
all_locations_table: list[MMARegion] = [
    MMARegion(
        "Peacock Purgatory",
        "CASTLE1",
        0x0CCB86,
        [
            # Amulets
            MMALocationData("Wocka Wocka Werebear Amulet - By tutorial flags"),
            MMALocationData("Wocka Wocka Werebear Amulet - On stairs near gardener"),
            MMALocationData("Wocka Wocka Werebear Amulet - On hill by lake"),
            MMALocationData("Wocka Wocka Werebear Amulet - By climbable wall"),
            MMALocationData("Muck Monster Amulet - By the lake"),
            MMALocationData("Muck Monster Amulet - Up climbable wall by Werebear Amulet", [AbilityFlag.CLIMB]),
            MMALocationData("Muck Monster Amulet - On path before climable wall"),
            MMALocationData("Muck Monster Amulet - Up climable wall by Muck Monster Amulet", [AbilityFlag.CLIMB]),
            MMALocationData("Noseferatu Amulet - Bottom of the lake", [AbilityFlag.SWIM]),
            MMALocationData("Noseferatu Amulet - By sundial"),
            MMALocationData("Noseferatu Amulet - Up super-jump platform"),
            MMALocationData("Noseferatu Amulet - Up stairs after triggering switch", [AbilityFlag.GLOVE]),
            # Energy
            MMALocationData("Evil Energy - 50%"),
            MMALocationData("Evil Energy - 100%", [AbilityFlag.CLIMB | AbilityFlag.GLIDE | AbilityFlag.SWIM]),
            # Tokens
            MMALocationData("1st Muppet Token"),
            MMALocationData("2nd Muppet Token"),
            MMALocationData("3rd Muppet Token"),
            MMALocationData("4th Muppet Token"),
            MMALocationData("5th Muppet Token", [AbilityFlag.CLIMB]),
            # Bonus
            MMALocationData("Bonus - B"),
            MMALocationData("Bonus - O"),
            MMALocationData("Bonus - N"),
            MMALocationData("Bonus - U"),
            MMALocationData("Bonus - S"),
        ],
    ),
    MMARegion(
        "Hallways of Doom",
        "CASTLE2",
        0x0CCBEE,
        [
            # Amulets
            MMALocationData("Ghoul-friend Amulet - Behind spawn"),
            MMALocationData("Ghoul-friend Amulet - On left staircase"),
            MMALocationData("Ghoul-friend Amulet - Top of left staircase"),
            MMALocationData("Ghoul-friend Amulet - Top of right staircase"),
            # Energy
            MMALocationData("Evil Energy - 50%", [AbilityFlag.SMASH]),
            MMALocationData("Evil Energy - 100%", [AbilityFlag.SMASH | AbilityFlag.CLIMB | AbilityFlag.GLIDE]),
            # Tokens
            MMALocationData("1st Muppet Token", [AbilityFlag.SMASH]),
            MMALocationData("2nd Muppet Token", [AbilityFlag.SMASH]),
            MMALocationData("3rd Muppet Token", [AbilityFlag.SMASH]),
            MMALocationData("4th Muppet Token", [AbilityFlag.SMASH | AbilityFlag.CLIMB]),
            MMALocationData("5th Muppet Token", [AbilityFlag.SMASH | AbilityFlag.CLIMB | AbilityFlag.GLIDE]),
            # Bonus
            MMALocationData("Bonus - B", [AbilityFlag.SMASH]),
            MMALocationData("Bonus - O", [AbilityFlag.SMASH | AbilityFlag.CLIMB]),
            MMALocationData("Bonus - N", [AbilityFlag.SMASH]),
            MMALocationData("Bonus - U", [AbilityFlag.SMASH | AbilityFlag.CLIMB | AbilityFlag.GLIDE]),
            MMALocationData("Bonus - S", [AbilityFlag.SMASH]),
        ],
    ),
    MMARegion(
        "Poker Faces",
        "CASTLE3",
        0x0CCC56,
        [
            # Amulets
            MMALocationData("Ker-monster Amulet - On lone pillar in lava"),
            MMALocationData("Ker-monster Amulet - By search light towers"),
            MMALocationData("Ker-monster Amulet - On trio of pillars in lava"),
            MMALocationData("Ker-monster Amulet - By pushable block"),
            # Energy
            MMALocationData("Evil Energy - 50%", [AbilityFlag.PUSH | AbilityFlag.GLIDE]),
            MMALocationData("Evil Energy - 100%", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
            # Tokens
            MMALocationData("1st Muppet Token", [AbilityFlag.PUSH | AbilityFlag.GLIDE]),
            MMALocationData("2nd Muppet Token", [AbilityFlag.PUSH | AbilityFlag.GLIDE]),
            MMALocationData("3rd Muppet Token", [AbilityFlag.PUSH | AbilityFlag.GLIDE]),
            MMALocationData("4th Muppet Token", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
            MMALocationData("5th Muppet Token", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
            # Bonus
            MMALocationData("Bonus - B"),
            MMALocationData("Bonus - O"),
            MMALocationData("Bonus - N", [AbilityFlag.PUSH | AbilityFlag.GLIDE]),
            MMALocationData("Bonus - U", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
            MMALocationData("Bonus - S", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
        ],
    ),
    MMARegion("Noseferatu", "CASTLEB", None, [MMALocationData("Boss defeated")]),
]

region_lookup: dict[str, MMARegion] = {x.name: x for x in all_locations_table}


def location_name_to_id(base_id: int) -> dict[str, int]:
    """Converts all locations from their `[Region: [Name: Data]]` format into `[Name: ID]`,
    where `ID` is a deterministic value greater than `base_id`."""
    result: dict[str, int] = {}
    for group_idx, region_data in enumerate(all_locations_table):
        for item_idx, location in enumerate(region_data.locations):
            result.update({f"{region_data.name} - {location.name}": base_id + group_idx + item_idx})
    return result


def location_name_groups() -> dict[str, set[str]]:
    """Converts all locations from their `[Region: [Name: Data]]` format into `[Region: [Name]]`."""
    result: dict[str, set[str]] = {}
    for region_data in all_locations_table:
        result[region_data.name] = {x.name for x in region_data.locations}
    return result
