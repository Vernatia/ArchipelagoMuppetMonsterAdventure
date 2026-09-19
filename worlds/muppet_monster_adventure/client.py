from typing import TYPE_CHECKING

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

from .constants import game_name


class MMAMorphState:
    def __init__(self) -> None:
        self.glide = False
        self.climb = False
        self.push = False
        self.swim = False
        self.smash = False

    def get_bytes(self) -> bytes:
        packed_data = (self.glide << 0) | (self.climb << 1) | (self.push << 2) | (self.swim << 3) | (self.smash << 4)
        return packed_data.to_bytes(2, "little")


class MMALevelState:
    # TODO: provide level memory location definitions
    def __init__(self) -> None:
        self.unlocked = False
        # TODO: figure out individual energy and token pickup triggers
        self.energy: int = 0
        self.tokens: int = 0


class MMAAmuletState:
    # TODO: maybe provide item identifier list
    def __init__(self, offset: int) -> None:
        self.flags = [False, False, False, False]
        self.offset = offset

    def process_changes(self, data: int) -> list[int]:
        new_flags = self.get_amulet_flags(data)
        changes: list[int] = []
        for i in range(4):
            if new_flags[i] and new_flags[i] != self.flags[i]:
                changes.append(i)
                self.flags[i] = True
        return changes

    def get_amulet_flags(self, data: int) -> list[bool]:
        # Note: amulets may not necessarily be placed in this order in the level.
        return [
            ((data >> self.offset) & 1) == 1,
            ((data >> self.offset + 1) & 1) == 1,
            ((data >> self.offset + 2) & 1) == 1,
            ((data >> self.offset + 3) & 1) == 1,
        ]


class MMAGameState:
    def __init__(self) -> None:
        self.morphs = MMAMorphState()
        self.levels: dict[str, MMALevelState] = {}
        self.amulets: dict[str, MMAAmuletState] = {
            "noseferatu": MMAAmuletState(16),
            "werebear": MMAAmuletState(20),
            "ker_monster": MMAAmuletState(8),
            "muck_monster": MMAAmuletState(12),
            "ghoul_friend": MMAAmuletState(0),
        }


class MMAClient(BizHawkClient):
    game = game_name
    system = "PSX"
    items_handling = 0b111

    def __init__(self):
        super().__init__()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # NTSC
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x009274, 11, "MainRAM")]))[0]).decode("ascii")
            if rom_name != "SLUS_012.38":
                # PAL
                rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x00928C, 11, "MainRAM")]))[0]).decode("ascii")
                if rom_name != "SCES_024.03":
                    return False
        except bizhawk.RequestFailedError:
            return False

        ctx.game = self.game
        ctx.items_handling = self.items_handling
        ctx.want_slot_data = True
        ctx.watcher_timeout = 0.125

        # State init
        self.last_amulets_flags: list[bytes] = [bytes(0)]
        self.level_name: str = ""
        self.game_state = MMAGameState()

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        from CommonClient import logger

        if await self.update_level_name(ctx):
            logger.info(f"Level changed to '{self.level_name}'")

        # TODO: PAL differences?
        amulets_flag = await bizhawk.read(ctx.bizhawk_ctx, [(0x0CCB78, 3, "MainRAM")])

        if amulets_flag != self.last_amulets_flags:
            self.last_amulets_flags = amulets_flag
            flags_int = int(amulets_flag[0].hex(), base=16)
            # Extract amulet pickup changes
            for name, state in self.game_state.amulets.items():
                changes = state.process_changes(flags_int)
                # TODO: emit location collection
                if len(changes) > 0:
                    logger.info(f"Amulet - '{name}' changes - {changes}")

        # Write powers
        await bizhawk.write(ctx.bizhawk_ctx, [(0x0B76F8, self.game_state.morphs.get_bytes(), "MainRAM")])
        return

    async def update_level_name(self, ctx: "BizHawkClientContext") -> bool:
        # TODO: not exactly sure how many bytes the name uses.
        level_bytes = (await bizhawk.read(ctx.bizhawk_ctx, [(0x0B87F8, 10, "MainRAM")]))[0]
        level_str = ""
        for b in level_bytes:
            # End of name string is denoted by null char.
            if b == 0:
                break
            level_str += chr(b)

        if level_str != self.level_name:
            self.level_name = level_str
            return True
        return False
