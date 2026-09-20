from typing import TYPE_CHECKING

from BaseClasses import Item, Location, MultiWorld, Region
from rule_builder import rules
from worlds.AutoWorld import World

from .client import *  # noqa: F403
from .items import ability_to_item, all_items_table, item_name_groups, item_name_to_id
from .locations import all_locations_table, location_name_groups, location_name_to_id
from .shared import LevelName, base_id, game_name


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

    origin_region_name = LevelName.HUB

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)

    def create_regions(self) -> None:
        super().create_regions()
        hub_region = Region(LevelName.HUB, self.player, self.multiworld)
        self.multiworld.regions.append(hub_region)
        regions: list[Region] = []
        for region_def in all_locations_table:
            region = Region(region_def.name, self.player, self.multiworld)
            _ = region.add_exits([LevelName.HUB])
            region.add_locations(
                {loc.full_identifier: location_name_to_id[loc.full_identifier] for loc in region_def.locations}
            )
            regions.append(region)
        self.multiworld.regions.extend(regions)
        _ = hub_region.add_exits([region.name for region in regions])
        return

    def create_items(self) -> None:
        super().create_items()
        self.multiworld.itempool += [
            MMAItem(item.name, item.classification, base_id + idx, self.player)
            for idx, item in enumerate(all_items_table)
        ]
        return

    def set_rules(self) -> None:
        super().set_rules()

        for region_def in all_locations_table:
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
