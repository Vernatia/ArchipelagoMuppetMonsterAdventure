from BaseClasses import Item, Location, MultiWorld, Region
from rule_builder import rules
from worlds.AutoWorld import World

from .client import *  # noqa: F403
from .items import (
    MMALevelItemData,
    ability_to_item,
    all_items_table,
    item_name_groups,
    item_name_to_id,
    max_level_index,
)
from .locations import all_locations_table, location_name_groups, location_name_to_id
from .shared import LevelName, game_name


class MMAItem(Item):
    game: str = game_name


class MMALocation(Location):
    game: str = game_name


class MuppetMonsterAdventureWorld(World):
    game = game_name

    topology_present = False  # Levels can be played in any order.

    item_name_to_id = item_name_to_id
    item_name_groups = item_name_groups
    location_name_to_id = location_name_to_id
    location_name_groups = location_name_groups

    origin_region_name = LevelName.HUB.value

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.starting_level: Item

    def get_filler_item_name(self) -> str:
        return "Nothing"

    def get_pre_fill_items(self) -> list["Item"]:
        return [self.starting_level]

    def pre_fill(self) -> None:
        super().pre_fill()
        self.push_precollected(self.starting_level)
        return

    def create_regions(self) -> None:
        super().create_regions()
        hub_region = Region(LevelName.HUB.value, self.player, self.multiworld)
        self.multiworld.regions.append(hub_region)
        regions: list[Region] = []
        for region_def in all_locations_table:
            region = Region(region_def.name, self.player, self.multiworld)
            region.add_locations(
                {loc.full_identifier: location_name_to_id[loc.full_identifier] for loc in region_def.locations}
            )
            regions.append(region)
        self.multiworld.regions.extend(regions)
        return

    def create_items(self) -> None:
        super().create_items()
        pool: list[Item] = []
        starter_level_index = self.random.randrange(0, max_level_index)
        for item_def in all_items_table:
            item = MMAItem(item_def.name, item_def.classification, item_name_to_id[item_def.name], self.player)
            if type(item_def) is not MMALevelItemData or item_def.index != starter_level_index:
                pool.append(item)
            else:
                self.starting_level = item

        self.multiworld.itempool += pool
        return

    def set_rules(self) -> None:
        super().set_rules()

        hub_region = self.get_region(LevelName.HUB.value)
        for region_def in all_locations_table:
            region = self.get_region(region_def.name)
            _ = hub_region.connect(region, None, rules.Has(region_def.name))
            _ = region.connect(hub_region, None, None)

            base_region_rule = rules.CanReachRegion(region_def.name)
            for location in region_def.locations:
                rule: rules.Rule = base_region_rule
                if location.ability_requirements is not None:
                    options: list[rules.Rule] = []
                    for option in location.ability_requirements:
                        items: list[str] = [ability_to_item[opt].name for opt in option]
                        options.append(rules.HasAll(*items))
                    rule = rules.And(rule, rules.Or(*options))
                self.set_rule(self.get_location(location.full_identifier), rule)

        return
