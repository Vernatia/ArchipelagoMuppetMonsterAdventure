from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

from .items import MMAAbilityItemData, MMALevelItemData, item_id_to_item
from .locations import LocationType, location_name_to_id, location_type_lookup, region_lookup
from .shared import AbilityFlag, game_name


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
        # TODO: level unlocking (starts at 0x0AA0C4)
        self.morphs: MMAMorphState = MMAMorphState()
        self.level_states: dict[str, MMALevelState] = {
            x.identifier: MMALevelState(x.state_address) for x in region_lookup.values() if x.state_address is not None
        }
        self.level_unlocks: list[bool] = [False for _ in region_lookup.values()]
        self.amulets: dict[LocationType, MMAAmuletState] = {
            LocationType.NOSEFERATU_AMULET: MMAAmuletState(0),
            LocationType.WEREBEAR_AMULET: MMAAmuletState(4),
            LocationType.KER_MONSTER_AMULET: MMAAmuletState(8),
            LocationType.MUCK_MONSTER_AMULET: MMAAmuletState(12),
            LocationType.GHOUL_FRIEND_AMULET: MMAAmuletState(16),
        }


class MMAClient(BizHawkClient):
    game = game_name
    system = "PSX"
    items_handling = 0b111
    patch_suffix = None

    def __init__(self):
        super().__init__()

        self.last_amulets_flags: list[bytes] = [bytes(0)]
        self.active_level_name: str = ""
        self.game_state: MMAGameState = MMAGameState()
        self.last_received_index = 0

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
        return True

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict[object, object]) -> None:
        super().on_package(ctx, cmd, args)  # pyright: ignore[reportUnknownMemberType]

        match cmd:
            case "Connected":
                # TODO: Read relevant slot data & reset state
                pass
            case _:
                pass
            # TODO: race countdown
        pass

    async def set_auth(self, ctx: "BizHawkClientContext") -> None:
        await ctx.get_username()

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        from CommonClient import logger

        # TODO: uncomment once dev testing done
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None or ctx.auth is None:
            return

        # TODO: first run should validate current state

        if await self.update_level_name(ctx):
            logger.info(f"Level changed to '{self.active_level_name}'")

        if (
            self.active_level_name == ""
            or self.active_level_name == "FRONT1"
            or self.active_level_name == "GLOBAL"
            or self.active_level_name.startswith("DEMO")
        ):
            # Not in-game
            return

        await self.check_locations(ctx)
        await self.receive_items(ctx)

        if self.active_level_name == "HUB":
            # Write level unlocks, always have all regions unlocked
            write_list: list[int] = [0xFF if unlocked else 0x00 for unlocked in self.game_state.level_unlocks]
            await bizhawk.write(ctx.bizhawk_ctx, [(0x0AA0C4, write_list, "MainRAM"), (0x0E22F0, [5], "MainRAM")])
        else:
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

    async def check_locations(self, ctx: "BizHawkClientContext") -> None:
        from CommonClient import logger

        # TODO: PAL differences?
        amulets_flag = await bizhawk.read(ctx.bizhawk_ctx, [(0x0CCB78, 3, "MainRAM")])
        if amulets_flag != self.last_amulets_flags:
            self.last_amulets_flags = amulets_flag
            flags_int = int.from_bytes(amulets_flag[0], byteorder="little")

            # Extract amulet pickup changes
            amulet_location_changes: list[int] = []
            for amulet_type, state in self.game_state.amulets.items():
                changes = state.process_changes(flags_int)
                # TODO: emit location collection
                if len(changes) > 0:
                    logger.info(f"'{amulet_type}' changes - {changes}")
                    for item in changes:
                        location = location_type_lookup[amulet_type][item]
                        ap_id = location_name_to_id[location.full_identifier]
                        amulet_location_changes.append(ap_id)

            if len(amulet_location_changes) > 0:
                # TODO: do we want to do anything with this information?
                _ = await ctx.check_locations(amulet_location_changes)

        if (level := self.game_state.level_states.get(self.active_level_name)) is not None:
            if await level.process_changes(ctx):
                logger.info(f"Level data updated - {level.print()}")
            pass
        # TODO: boss defeated check. Will need to validate the number change once

    async def receive_items(self, ctx: "BizHawkClientContext") -> None:
        new_items = ctx.items_received[self.last_received_index :]
        if len(new_items) == 0:
            return

        for net_item in new_items:
            item = item_id_to_item[net_item.item]
            match item:
                case MMAAbilityItemData():
                    match item.ability_type:
                        case AbilityFlag.GLIDE:
                            self.game_state.morphs.glide = True
                        case AbilityFlag.CLIMB:
                            self.game_state.morphs.climb = True
                        case AbilityFlag.PUSH:
                            self.game_state.morphs.push = True
                        case AbilityFlag.SWIM:
                            self.game_state.morphs.swim = True
                        case AbilityFlag.SMASH:
                            self.game_state.morphs.smash = True
                        case _:
                            # TODO: glove & spin
                            pass
                case MMALevelItemData():
                    self.game_state.level_unlocks[item.index] = True
                    pass
                case _:
                    pass

        self.last_received_index = len(ctx.items_received) - 1
        pass
