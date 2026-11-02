from typing import TYPE_CHECKING
from .addresses.structs import AddressTable
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from . import BizHawkClientContext

class MessageDisplay:
    addressTable: AddressTable
    levelMessageUpdated: bool = False

    def __init__(self, addressTable: AddressTable):
        self.addressTable = addressTable

    def convertMemoryAddress(self, address: bytes):
        """Converts a memory address from bytes into the equivalent int"""
        i = int.from_bytes(address)
        return int.from_bytes(i.to_bytes(3, 'little'))

    def revertMemoryAddress(self, address: int):
        """Reverts an int address to Big Endian"""
        return address.to_bytes(3, 'big')

    async def writeToMemory(self, ctx: "BizHawkClientContext", messages: list, addresses: list):
        """Write messages to addresses, messages will be joined by new line, and the result written to all addresses"""
        outputMessage = bytearray(messages.pop(0), 'ASCII')
        for message in messages:
            outputMessage.extend(b'\x0A')
            outputMessage.extend(message.encode('ASCII'))

        outputMessage.extend(b'\x00')

        outputAddresses = list()
        for address in addresses:
            outputAddresses.append((address, outputMessage, "MainRAM"))

        await bizhawk.write(ctx.bizhawk_ctx, outputAddresses)

    async def updateHubMessage(self, ctx: "BizHawkClientContext"):
        await self.writeToMemory(
            ctx,
            ['Loading retrieved items... Loading... Loading... Loading... Loading... Loading... Loading... Loading...'],
            [self.addressTable.level_hub_message]
        )
        self.levelMessageUpdated = True

    async def disablePepeNonMinigames(self, ctx: "BizHawkClientContext", levelName: str):
        """Disables the Pepe message pointers so non-minigames don't flicker the UI"""
        # Two Reads + One Write (With one Read and the Write being batches)
        
        if levelName not in self.addressTable.level_minigame_data:
            return

        gameAddresses = self.addressTable.level_minigame_data[levelName]

        # Pepe's messages are 4 byte + 4 byte, where the second 4 byte is the memory address of the message to load
        initialMemoryAddress = self.addressTable.pepe_message_pointer_start
        # Step to the next address so we know what the first memory location is
        initialMessageAddress = (initialMemoryAddress + 4)
        # Grab the memory address of the first message
        data = await bizhawk.read(
                ctx.bizhawk_ctx,
                [(initialMessageAddress, 4, "MainRAM")]
            )
        firstMessageAddress = data[0]
        # Remove the 80 byte
        firstMessageAddress = firstMessageAddress[:-1]
        converted = self.convertMemoryAddress(firstMessageAddress)

        # Populate an array containing all the memory locations for Pepe's messages
        pepeMessages = []
        nextAddress = initialMessageAddress
        while nextAddress < converted:
            pepeMessages.append((nextAddress, 4, "MainRAM"))
            nextAddress = nextAddress + 8

        messageData = await bizhawk.read(ctx.bizhawk_ctx, pepeMessages)

        # Now figure out which ones aren't Mini-game pointers, and turn the others off
        clearPointers = []
        index = 0
        for address in messageData:
            address = address[:-1]
            converted = self.convertMemoryAddress(address)
            isMiniGame = False
            for minigame in gameAddresses.minigames:
                if converted == minigame.start or converted == minigame.retry:
                    isMiniGame = True
                    break

            if not isMiniGame:
                clearPointers.append((pepeMessages[index][0], (0).to_bytes(4, "little"), "MainRAM"))

            index = index + 1

        await bizhawk.write(ctx.bizhawk_ctx, clearPointers)

    async def updateMiniGameMessages(self, ctx: "BizHawkClientContext", levelName: str):
        """Sets the Start Message for all mini-games to a known string"""
        if levelName not in self.addressTable.level_minigame_data:
            return
        
        gameAddresses = self.addressTable.level_minigame_data[levelName]

        for minigame in gameAddresses.minigames:
            # Add a custom message for each mini-game
            await self.writeToMemory(
                ctx,
                [
                    minigame.name,
                    'Press % to play or & to cancel.'
                ], [
                    minigame.start,
                    minigame.retry
                ]
            )

        self.levelMessageUpdated = True

    async def clearPepeMessage(self, ctx: "BizHawkClientContext"):
        await bizhawk.write(
                ctx.bizhawk_ctx,
                [
                    (self.addressTable.pepe_message_ui_counter, (0).to_bytes(4, "little"), "MainRAM"),
                    (self.addressTable.pepe_message_message_pointer, (0).to_bytes(4, "little"), "MainRAM"),
                ],
            )

    async def disablePepeMessages(self, ctx: "BizHawkClientContext", levelName: str):
        """Disables Pepe's UI messages"""
        data = await bizhawk.read(
            ctx.bizhawk_ctx,
            [(self.addressTable.pepe_message_message_pointer, 4, "MainRAM")]
        )

        messageAddress = data[0]
        # strip the \x80 from the message address pointer
        messageAddress = messageAddress[:-1]

        # Ignore any "blank" messages
        if messageAddress == b'\x00\x00\x00':
            return
        converted = self.convertMemoryAddress(messageAddress)
        
        # Ignore any levels that aren't valid
        if levelName not in self.addressTable.level_minigame_data:
            await self.clearPepeMessage(ctx)
            return

        gameAddresses = self.addressTable.level_minigame_data[levelName]

        isMiniGame = False
        for minigame in gameAddresses.minigames:
            if converted == minigame.start or converted == minigame.retry:
                isMiniGame = True
                break

        # don't block mini-game messages
        if isMiniGame:
            return

        await self.clearPepeMessage(ctx)

    def getLevelUpdated(self):
        """Returns whether or not the level messages function has run"""
        return self.levelMessageUpdated

    def levelHasChanged(self):
        """Clears the levels messages updated flag"""
        self.levelMessageUpdated = False