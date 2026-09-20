from enum import Flag, auto

base_id: int = 25_899_560
game_name: str = "Muppet Monster Adventure"


class AbilityFlag(Flag):
    GLIDE = auto()
    CLIMB = auto()
    PUSH = auto()
    SWIM = auto()
    SMASH = auto()
    # TODO: implement these (if possible)
    GLOVE = auto()
    SPIN = auto()
