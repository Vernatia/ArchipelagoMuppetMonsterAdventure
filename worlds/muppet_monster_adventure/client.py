from typing import TYPE_CHECKING

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

from .constants import game_name


class MMAFlagField:
    def __init__(self, size: int, offset: int) -> None:
        self.size: int = size
        self.offset: int = offset
        self.flags: list[bool] = [False] * size

    def split_flags(self, data: int) -> list[bool]:
        new_flags: list[bool] = [False] * self.size
        for i in range(self.size):
            new_flags[i] = ((data >> self.offset + i) & 1) == 1
        return new_flags

    def process_changes(self, data: int) -> list[int]:
        new_flags = self.split_flags(data)
        changes: list[int] = []
        for i in range(self.size):
            if new_flags[i] and new_flags[i] != self.flags[i]:
                changes.append(i)
                self.flags[i] = True
        return changes


class MMAMorphState:
    def __init__(self) -> None:
        self.glide: bool = False
        self.climb: bool = False
        self.push: bool = False
        self.swim: bool = False
        self.smash: bool = False

    def get_bytes(self) -> bytes:
        packed_data = (self.glide << 0) | (self.climb << 1) | (self.push << 2) | (self.swim << 3) | (self.smash << 4)
        return packed_data.to_bytes(2, "little")


class MMALevelState:
    def __init__(
        self,
        address: int,
    ) -> None:
        self.address: int = address
        self.unlocked: bool = False
        self.bonus: MMAFlagField = MMAFlagField(size=5, offset=0)
        self.coins: int = 0
        self.tokens: int = 0
        self.energy: int = 0

    # TODO: what return?
    async def process_changes(self, ctx: "BizHawkClientContext") -> bool:
        # TODO: technically we could do visit-sanity if we wanted, since the game tracks it.
        # Would need to adjust all of this though, since it's 2 bytes prior to the Bonus.
        data = (await bizhawk.read(ctx.bizhawk_ctx, [(self.address, 6, "MainRAM")]))[0]
        bonus_changes = self.bonus.process_changes(data[0])
        tokens = data[1]
        coins = int.from_bytes(data[2:4], byteorder="little")
        energy = int.from_bytes(data[4:6], byteorder="little")

        has_change: bool = False
        if len(bonus_changes) > 0 or tokens > self.tokens or coins > self.coins or energy > self.energy:
            has_change = True

        # Sometimes fields like these are flipped up and down for effect.
        # Don't know if these specifically are, but better safe than sorry.
        self.tokens = max(tokens, self.tokens)
        self.coins = max(coins, self.coins)
        self.energy = max(energy, self.energy)
        return has_change

    def print(self) -> str:
        return f"Tokens: {self.tokens}, Energy: {self.energy}, Bonus: {self.bonus.flags}"


class MMAAmuletState:
    # TODO: maybe provide item identifier list
    def __init__(self, offset: int) -> None:
        self.flags: MMAFlagField = MMAFlagField(4, offset)

    def process_changes(self, data: int) -> list[int]:
        return self.flags.process_changes(data)


class MMAGameState:
    def __init__(self) -> None:
        self.morphs: MMAMorphState = MMAMorphState()
        self.levels: dict[str, MMALevelState] = {"CASTLE1": MMALevelState(0x0CCB86)}
        self.amulets: dict[str, MMAAmuletState] = {
            "noseferatu": MMAAmuletState(0),
            "werebear": MMAAmuletState(4),
            "ker_monster": MMAAmuletState(8),
            "muck_monster": MMAAmuletState(12),
            "ghoul_friend": MMAAmuletState(16),
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
        self.active_level_name: str = ""
        self.game_state: MMAGameState = MMAGameState()

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        from CommonClient import logger

        # TODO: first run should validate current state

        if await self.update_level_name(ctx):
            logger.info(f"Level changed to '{self.active_level_name}'")

        # TODO: PAL differences?
        amulets_flag = await bizhawk.read(ctx.bizhawk_ctx, [(0x0CCB78, 3, "MainRAM")])
        if amulets_flag != self.last_amulets_flags:
            self.last_amulets_flags = amulets_flag
            flags_int = int.from_bytes(amulets_flag[0], byteorder="little")
            # Extract amulet pickup changes
            for name, state in self.game_state.amulets.items():
                changes = state.process_changes(flags_int)
                # TODO: emit location collection
                if len(changes) > 0:
                    logger.info(f"Amulet - '{name}' changes - {changes}")

        if (level := self.game_state.levels.get(self.active_level_name)) is not None:
            if await level.process_changes(ctx):
                logger.info(f"Level data updated - {level.print()}")
            pass

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

        if level_str != self.active_level_name:
            self.active_level_name = level_str
            return True
        return False
