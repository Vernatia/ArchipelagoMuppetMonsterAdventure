from collections.abc import Sequence
from enum import Enum, StrEnum
from typing import NamedTuple

from .shared import AbilityFlag, AmuletType, LevelName, any_weapon_flag, base_id


class LocationType(Enum):
    NOSEFERATU_AMULET = AmuletType.NOSEFERATU_AMULET.value
    WEREBEAR_AMULET = AmuletType.WEREBEAR_AMULET.value
    KER_MONSTER_AMULET = AmuletType.KER_MONSTER_AMULET.value
    MUCK_MONSTER_AMULET = AmuletType.MUCK_MONSTER_AMULET.value
    GHOUL_FRIEND_AMULET = AmuletType.GHOUL_FRIEND_AMULET.value
    ENERGY = "Evil Energy"
    TOKEN = "Muppet Token"
    BONUS = "Bonus letter"
    BOSS = "Boss defeated"


class MMALocationData:
    ability_requirements: list[AbilityFlag] | None

    def __init__(
        self,
        type: LocationType,
        name: str,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        self.name: str = name
        self.type: LocationType = type
        # Each flag lists the unique combination of abilities which unlocks this location.
        # Alternatives should be provided as a separate entry.
        # e.g. The location can be unlocked by either "climb and swim" OR "climb and glide".
        # This would be represented as: [AbilityFlag.CLIMB | AbilityFlag.SWIM, AbilityFlag.CLIMB | AbilityFlag.GLIDE]
        self.ability_requirements = ability_requirements
        self.full_identifier: str = ""

    def ap_id(self) -> int:
        return location_name_to_id[self.full_identifier]


class MMABossLocationData(MMALocationData):
    def __init__(
        self,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        super().__init__(LocationType.BOSS, "Boss defeated", ability_requirements)


class EnergyAmount(StrEnum):
    HALF = "50%"
    FULL = "100%"


class MMAEnergyLocationData(MMALocationData):
    def __init__(
        self,
        amount: EnergyAmount,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        super().__init__(LocationType.ENERGY, f"{LocationType.ENERGY.value} - {amount.value}", ability_requirements)


class BonusLetterType(StrEnum):
    B = "B"
    O = "O"
    N = "N"
    U = "U"
    S = "S"


class MMABonusLetterLocationData(MMALocationData):
    def __init__(
        self,
        letter: BonusLetterType,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        super().__init__(LocationType.BONUS, f"{LocationType.BONUS.value} - {letter.value}", ability_requirements)


class MMAMuppetTokenLocationData(MMALocationData):
    def __init__(
        self,
        name: str,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        super().__init__(LocationType.TOKEN, f"{LocationType.TOKEN.value} - {name}", ability_requirements)


class MMAAmuletLocationData(MMALocationData):
    def __init__(
        self,
        type: AmuletType,
        name: str,
        ability_requirements: list[AbilityFlag] | None = None,
    ):
        location_type = LocationType(type.value)
        super().__init__(location_type, f"{type.value} - {name}", ability_requirements)


class MMARegion:
    def __init__(
        self,
        name: LevelName,
        ingame_identifier: str,
        energy_count: int,
        locations: list[MMALocationData],
    ) -> None:
        self.name: str = name.value
        self.ingame_identifier: str = ingame_identifier
        self.energy_count: int = energy_count
        self.locations: list[MMALocationData] = locations
        pass


class EnergyLocationData(NamedTuple):
    total_energy: int
    half: list[AbilityFlag] | None
    full: list[AbilityFlag] | None


class BonusLocationData(NamedTuple):
    b: list[AbilityFlag] | None
    o: list[AbilityFlag] | None
    n: list[AbilityFlag] | None
    u: list[AbilityFlag] | None
    s: list[AbilityFlag] | None
    # We may not always be able to infer the requirements for this, since it could be off the path
    token: list[AbilityFlag] | None


class TokenLocationData(NamedTuple):
    name: str
    requirements: list[AbilityFlag] | None = None


class MMALevelRegion(MMARegion):
    def __init__(
        self,
        name: LevelName,
        ingame_identifier: str,
        energy_data: EnergyLocationData,
        bonus_data: BonusLocationData,
        token_data: list[TokenLocationData],
        additional_locations: Sequence[MMALocationData] | None = None,
    ) -> None:
        locations: list[MMALocationData] = [
            *[
                MMAEnergyLocationData(EnergyAmount.HALF, energy_data.half),
                MMAEnergyLocationData(EnergyAmount.FULL, energy_data.full),
            ],
            *[
                MMABonusLetterLocationData(BonusLetterType.B, bonus_data.b),
                MMABonusLetterLocationData(BonusLetterType.O, bonus_data.o),
                MMABonusLetterLocationData(BonusLetterType.N, bonus_data.n),
                MMABonusLetterLocationData(BonusLetterType.U, bonus_data.u),
                MMABonusLetterLocationData(BonusLetterType.S, bonus_data.s),
            ],
            *[
                MMAMuppetTokenLocationData(token.name, token.requirements)
                for token in [*token_data, TokenLocationData("BONUS", bonus_data.token)]  # Append the bonus token
            ],
            *(additional_locations if additional_locations is not None else []),
        ]
        super().__init__(name, ingame_identifier, energy_data.total_energy, locations)
        pass


class MMABossRegion(MMARegion):
    def __init__(
        self,
        name: LevelName,
        ingame_identifier: str,
        locations: list[MMALocationData],
    ) -> None:
        super().__init__(name, ingame_identifier, 0, locations)


# TODO: currently we're assuming checks can be done without caring about taking damage
# The iframes are very lenient, allowing you to get past basically every enemy,
# and the levels tend to have a good number of recovery hearts.
# BUT!! (and this is a big BUTT) the game does get notably harder to play this way after zone 1.
# Playtesting is required here...

# TODO: tokens are no longer a count, but individual locations.

# Note: The order of basically all of these matters, since the client depends on this to check world state.
all_locations_table: list[MMARegion] = [
    MMALevelRegion(
        LevelName.PEACOCK_PURGATORY,
        "CASTLE1",
        EnergyLocationData(
            total_energy=300,
            half=[AbilityFlag.GLOVE, AbilityFlag.SPIN, AbilityFlag.GLIDE, AbilityFlag.CLIMB, AbilityFlag.SWIM],
            full=[AbilityFlag.CLIMB | AbilityFlag.GLIDE | AbilityFlag.SWIM | AbilityFlag.GLOVE | AbilityFlag.SPIN],
        ),
        BonusLocationData(
            b=None,
            o=None,
            n=None,
            u=None,
            s=[AbilityFlag.GLIDE, AbilityFlag.GLOVE],  # Bat switch platform
            token=[AbilityFlag.GLIDE, AbilityFlag.GLOVE],
        ),
        [
            TokenLocationData("By exit"),
            TokenLocationData("Up Super Jump Pad"),
            TokenLocationData("Race Percy"),
            TokenLocationData("Sunflower minigame", [AbilityFlag.GLIDE | AbilityFlag.CLIMB]),
        ],
        [
            # Note: these are ordered by their bitwise flag position (per type)
            # Werebear
            MMAAmuletLocationData(AmuletType.WEREBEAR_AMULET, "By tutorial flags"),
            MMAAmuletLocationData(AmuletType.WEREBEAR_AMULET, "By climbable wall"),
            MMAAmuletLocationData(AmuletType.WEREBEAR_AMULET, "On hill by lake"),
            MMAAmuletLocationData(AmuletType.WEREBEAR_AMULET, "On stairs near gardener"),
            # Muck Monster
            MMAAmuletLocationData(
                AmuletType.MUCK_MONSTER_AMULET, "Up climbable wall by Werebear Amulet", [AbilityFlag.CLIMB]
            ),
            MMAAmuletLocationData(
                AmuletType.MUCK_MONSTER_AMULET, "Up climable wall above other Muck Monster Amulet", [AbilityFlag.CLIMB]
            ),
            MMAAmuletLocationData(AmuletType.MUCK_MONSTER_AMULET, "Along the cliff trail"),
            MMAAmuletLocationData(AmuletType.MUCK_MONSTER_AMULET, "By the lake"),
            # Noseferatu
            MMAAmuletLocationData(AmuletType.NOSEFERATU_AMULET, "Up Super Jump Pad"),
            MMAAmuletLocationData(AmuletType.NOSEFERATU_AMULET, "Bottom of the lake", [AbilityFlag.SWIM]),
            MMAAmuletLocationData(
                AmuletType.NOSEFERATU_AMULET,
                "Up stairs after triggering switch",
                [AbilityFlag.GLOVE, AbilityFlag.GLIDE],
            ),
            MMAAmuletLocationData(AmuletType.NOSEFERATU_AMULET, "By sundial"),
        ],
    ),
    MMALevelRegion(
        LevelName.HALLWAYS_OF_DOOM,
        "CASTLE2",
        EnergyLocationData(
            total_energy=320,
            half=[AbilityFlag.SMASH | AbilityFlag.GLOVE],  # Bat switch locks off like 70% of the level
            full=[AbilityFlag.SMASH | AbilityFlag.CLIMB | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.SPIN],
        ),
        BonusLocationData(
            b=[AbilityFlag.SMASH],
            o=[AbilityFlag.SMASH | AbilityFlag.CLIMB],
            n=[AbilityFlag.SMASH | AbilityFlag.GLOVE],
            u=[AbilityFlag.SMASH | AbilityFlag.GLOVE | AbilityFlag.CLIMB | AbilityFlag.GLIDE],
            s=[AbilityFlag.SMASH | AbilityFlag.GLOVE],
            token=[AbilityFlag.SMASH | AbilityFlag.GLOVE | AbilityFlag.CLIMB],
        ),
        [
            TokenLocationData("Rizzo", any_weapon_flag(AbilityFlag.SMASH)),
            TokenLocationData("On top of the bookshelves", [AbilityFlag.SMASH | AbilityFlag.GLOVE | AbilityFlag.CLIMB]),
            TokenLocationData("Smashing minigame", [AbilityFlag.SMASH | AbilityFlag.GLOVE]),
            TokenLocationData("Near smashable door", [AbilityFlag.SMASH | AbilityFlag.GLOVE]),
        ],
        [
            # Amulets
            MMAAmuletLocationData(AmuletType.GHOUL_FRIEND_AMULET, "Behind spawn"),
            MMAAmuletLocationData(AmuletType.GHOUL_FRIEND_AMULET, "On left staircase"),
            MMAAmuletLocationData(AmuletType.GHOUL_FRIEND_AMULET, "Top of left staircase"),
            MMAAmuletLocationData(AmuletType.GHOUL_FRIEND_AMULET, "Top of right staircase"),
        ],
    ),
    MMALevelRegion(
        LevelName.POKER_FACES,
        "CASTLE3",
        EnergyLocationData(
            total_energy=350,
            half=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE],
            full=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.CLIMB],
        ),
        BonusLocationData(
            b=None,
            o=None,
            n=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE],
            u=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.CLIMB],
            s=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.CLIMB],
            token=[AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.CLIMB],
        ),
        [
            TokenLocationData("Target shooting minigame", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE]),
            TokenLocationData("Standing pillar by start", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE]),
            TokenLocationData(
                "Block minigame", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.SPIN]
            ),
            TokenLocationData(
                "Glide to the rooftop", [AbilityFlag.PUSH | AbilityFlag.GLIDE | AbilityFlag.GLOVE | AbilityFlag.CLIMB]
            ),
        ],
        [
            # Amulets
            MMAAmuletLocationData(AmuletType.KER_MONSTER_AMULET, "On lone pillar in lava"),
            MMAAmuletLocationData(AmuletType.KER_MONSTER_AMULET, "By search light towers"),
            MMAAmuletLocationData(AmuletType.KER_MONSTER_AMULET, "By pushable block"),
            MMAAmuletLocationData(AmuletType.KER_MONSTER_AMULET, "On trio of pillars in lava"),
        ],
    ),
    MMABossRegion(
        LevelName.NOSEFERATU_BITES_BACK,
        "CASTLEB",
        [MMABossLocationData([AbilityFlag.GLOVE])],
    ),
    MMARegion(
        LevelName.GRAVE_MATTERS,
        "GRVYARD1",
        350,
        [],
    ),
    MMARegion(
        LevelName.MOLTEN_MAYHEM,
        "GRVYARD2",
        380,
        [],
    ),
    MMARegion(
        LevelName.SHIVERING_TIMBER_SHOALS,
        "GRVYARD3",
        400,
        [],
    ),
    MMABossRegion(
        LevelName.BEE_WARE_THE_WEREBEAR,
        "GRVYARDB",
        [MMABossLocationData([AbilityFlag.SPIN])],
    ),
]

# Maps region name to the region data definition
region_lookup: dict[str, MMARegion] = {region.name: region for region in all_locations_table}
non_boss_region_lookup: dict[str, MMARegion] = {
    region.name: region for region in all_locations_table if type(region) is MMARegion
}

# Lists all locations, by type
location_type_lookup: dict[LocationType, list[MMALocationData]] = {}
location_type_lookup_by_region: dict[str, dict[LocationType, list[MMALocationData]]] = {}
for region in all_locations_table:
    for loc in region.locations:
        location_type_lookup.update({loc.type: (location_type_lookup.get(loc.type) or []) + [loc]})
        # Store by region for level-based locations
        region_entry = location_type_lookup_by_region.get(region.name) or {}
        region_entry.update({loc.type: (region_entry.get(loc.type) or []) + [loc]})
        location_type_lookup_by_region.update({region.name: region_entry})

# Maps locations to their AP identifier
location_name_to_id: dict[str, int] = {}
__running_idx = 0
for region_data in all_locations_table:
    for location in region_data.locations:
        location.full_identifier = f"{region_data.name}: {location.name}"
        location_name_to_id.update({location.full_identifier: base_id + __running_idx})
        __running_idx += 1

# Groups locations by region
location_name_groups: dict[str, set[str]] = {}
for region_data in all_locations_table:
    location_name_groups[region_data.name] = {x.name for x in region_data.locations}
