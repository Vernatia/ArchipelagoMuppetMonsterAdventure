from typing import TYPE_CHECKING
from .addresses.structs import AddressTable
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from . import BizHawkClientContext

class MessageDisplay:
    addressTable: AddressTable

    def __init__(self, addressTable: AddressTable):
        self.addressTable = addressTable

    async def disablePepeMessages(self, ctx: "BizHawkClientContext"):
        """Disables Pepe's UI messages"""
        """TODO: Fix this to not disable Mini-Fames"""
        await bizhawk.write(
                ctx.bizhawk_ctx,
                [
                    (self.addressTable.pepe_message_ui_counter, (0).to_bytes(4, "little"), "MainRAM"),
                    #(addressTable.pepe_message_ui_pointer, (0).to_bytes(4, "little"), "MainRAM"),
                    (self.addressTable.pepe_message_message_pointer, (0).to_bytes(4, "little"), "MainRAM"),
                ],
            )

