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

    def __init__(self, name: str, ability_type: AbilityFlag, classification: ItemClassification) -> None:
        super().__init__(name, classification)
        self.ability_type: AbilityFlag = ability_type


@final
class MMALevelItemData(MMAItemData):
    group = "Levels"

    def __init__(self, name: LevelName, classification: ItemClassification) -> None:
        super().__init__(name.value, classification)
        self.index: int = 0


@final
class MMAFillerItemData(MMAItemData):
    group = "Filler"


all_items_table: Sequence[MMAItemData] = [
    # Filler
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    MMAFillerItemData("Nothing", ItemClassification.filler),
    # Abilities
    MMAAbilityItemData("Gliding", AbilityFlag.GLIDE, ItemClassification.progression),
    MMAAbilityItemData("Climbing", AbilityFlag.CLIMB, ItemClassification.progression),
    MMAAbilityItemData("Block Pushing", AbilityFlag.PUSH, ItemClassification.progression),
    MMAAbilityItemData("Swimming", AbilityFlag.SWIM, ItemClassification.progression),
    MMAAbilityItemData("Smashing", AbilityFlag.SMASH, ItemClassification.progression),
    # TODO: figure out how to lock these (if possible)
    # MMAItemData("Power Glove", IC.progression),
    # MMAItemData("Spin", IC.progression),
    # Levels
    MMALevelItemData(LevelName.PEACOCK_PURGATORY, ItemClassification.progression),
    MMALevelItemData(LevelName.HALLWAYS_OF_DOOM, ItemClassification.progression),
    MMALevelItemData(LevelName.POKER_FACES, ItemClassification.progression),
    MMALevelItemData(LevelName.NOSEFERATU, ItemClassification.progression),
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
