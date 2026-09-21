from abc import ABC
from collections.abc import Sequence
from typing import ClassVar, final

from BaseClasses import ItemClassification

from .shared import AbilityFlag, LevelName, base_id


class MMAItemData(ABC):
    group: ClassVar[str]

    def __init__(self, name: str, classification: ItemClassification) -> None:
        self.name: str = name
        self.classification: ItemClassification = classification
        pass


@final
class MMAAbilityItemData(MMAItemData):
    group = "Abilities"

    def __init__(self, name: str, ability_type: AbilityFlag) -> None:
        super().__init__(name, ItemClassification.progression)
        self.ability_type: AbilityFlag = ability_type


@final
class MMALevelItemData(MMAItemData):
    group = "Levels"

    def __init__(self, name: LevelName) -> None:
        super().__init__(name.value, ItemClassification.progression)
        self.index: int = 0


@final
class MMAFillerItemData(MMAItemData):
    group = "Filler"

    def __init__(self, name: str) -> None:
        super().__init__(name, ItemClassification.filler)


filler_items_table: list[MMAFillerItemData] = [
    MMAFillerItemData("Nothing"),
]

all_items_table: Sequence[MMAItemData] = [
    # Abilities
    MMAAbilityItemData("Gliding", AbilityFlag.GLIDE),
    MMAAbilityItemData("Climbing", AbilityFlag.CLIMB),
    MMAAbilityItemData("Block Pushing", AbilityFlag.PUSH),
    MMAAbilityItemData("Swimming", AbilityFlag.SWIM),
    MMAAbilityItemData("Smashing", AbilityFlag.SMASH),
    # TODO: figure out how to lock these (if possible)
    # MMAItemData("Power Glove", IC.progression),
    # MMAItemData("Spin", IC.progression),
    # Levels
    MMALevelItemData(LevelName.PEACOCK_PURGATORY),
    MMALevelItemData(LevelName.HALLWAYS_OF_DOOM),
    MMALevelItemData(LevelName.POKER_FACES),
    MMALevelItemData(LevelName.NOSEFERATU),
    *filler_items_table,
]

item_name_to_id: dict[str, int] = {}
item_id_to_item: dict[int, MMAItemData] = {}
ability_to_item: dict[AbilityFlag, MMAItemData] = {}
max_level_index = 0
for idx, item in enumerate(all_items_table):
    item_name_to_id.update({str(item.name): base_id + idx})
    item_id_to_item.update({base_id + idx: item})
    if type(item) is MMALevelItemData:
        item.index = max_level_index
        max_level_index += 1
    elif type(item) is MMAAbilityItemData:
        ability_to_item.update({item.ability_type: item})

item_name_groups: dict[str, set[str]] = {}
for item in all_items_table:
    name: str = ""
    item_name_groups.update({item.group: (item_name_groups.get(item.group) or set()) | {item.name}})
