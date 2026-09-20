from typing import NamedTuple

from BaseClasses import ItemClassification as IC

from .constants import base_id


class MMAItemData:
    def __init__(self, name: str, classification: IC) -> None:
        self.name: str = name
        self.classification: IC = classification
        pass


abilities_table: list[MMAItemData] = [
    MMAItemData("Climbing", IC.progression),
    MMAItemData("Swimming", IC.progression),
    MMAItemData("Gliding", IC.progression),
    MMAItemData("Block Pushing", IC.progression),
    MMAItemData("Smashing", IC.progression),
    # TODO: figure out how to lock these (if possible)
    # MMAItemData("Power Glove", IC.progression),
    # MMAItemData("Spin", IC.progression),
]

levels_table: list[MMAItemData] = [
    MMAItemData("Peacock Purgatory", IC.progression),
    MMAItemData("Hallways of Doom", IC.progression),
    MMAItemData("Poker Faces", IC.progression),
    MMAItemData("Noseferatu", IC.progression),
    # TODO: other levels
]

all_items_table: dict[str, list[MMAItemData]] = {
    "Abilities": abilities_table,
    "Levels": levels_table,
}

item_name_to_id: dict[str, int] = {}
__running_idx = 0
for group_items in all_items_table.values():
    for item in group_items:
        item_name_to_id.update({item.name: base_id + __running_idx})
        __running_idx += 1

item_name_groups: dict[str, set[str]] = {}
for group_name, group_items in all_items_table.items():
    item_name_groups[group_name] = {item.name for item in group_items}
