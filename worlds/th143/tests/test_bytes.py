import unittest

import pymem

from BaseClasses import MultiWorld
from ..variables.asm_code_address import ADDR_STATIC_ITEM_UPGRADES, ADDR_STATIC_MALLET_SUB4, ADDR_STATIC_MALLET_SUB3


def getPointerAddress(pm, base, offsets):
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset
    return pm.read_uint(address) + offsets[-1]


class ISCStatTest(unittest.TestCase):
    multiworld: MultiWorld

    def test_disable_item_level_up(self):
        self.pm = pymem.Pymem(process_name="th143.exe")
        for offset in ADDR_STATIC_ITEM_UPGRADES:
            self.pm.write_bytes(self.pm.base_address + offset, bytes([0xEB]), 1)
        for offset_4byte in ADDR_STATIC_MALLET_SUB4:
            self.pm.write_bytes(self.pm.base_address + offset_4byte, bytes([0x90, 0x90, 0x90, 0x90]), 4)
        for offset_3byte in ADDR_STATIC_MALLET_SUB3:
            self.pm.write_bytes(self.pm.base_address + offset_3byte, bytes([0x90, 0x90, 0x90]), 3)
        print("Disabled all cheat item upgrades!")

    def test_unlock_day_one(self):
        self.pm = pymem.Pymem(process_name="th143.exe")
        addrDayOneClear = getPointerAddress(self.pm, self.pm.base_address + 0xE6B9C, [0xEFB8])
        self.pm.write_bytes(addrDayOneClear, bytes([0x01]), 1)

    def test_set_sub_item(self):
        # Change between True and False to unlock and lock sub-items, respectively.
        self.pm = pymem.Pymem(process_name="th143.exe")
        cheat_sub_item_unlocked: bool = False

        addrSubItemData = getPointerAddress(self.pm, self.pm.base_address + 0xE6B9C, [0xEFAD])
        self.pm.write_bool(addrSubItemData, cheat_sub_item_unlocked)
        self.pm.write_bool(self.pm.base_address + 0xE4728, cheat_sub_item_unlocked)

    def test_set_item_stats(self):
        self.pm = pymem.Pymem(process_name="th143.exe")

        # 0 Nimble Fabric
        # 1 Tengu's Toy Camera
        # 2 Gap Folding Umbrella
        # 3 Ghastly Send-off Lantern
        # 4 Bloodthirsty Yin-yang Orb
        # 5 Four-Foot Magic Bomb
        # 6 Substitute Jizo
        # 7 Cursed Decoy Doll
        # 8 Miracle Mallet Replica
        cheat_item_id = 0
        cheat_item_level = 7 # purely cosmetic
        cheat_item_unique_stat = 500
        # See Touhou Wiki for what each item's unique stat is.
        # For items that use time as their unique stat, 60 = 1 second.
        # Bloodthirsty Yin-yang Orb's unique stat only ever stays at 60 in the vanilla game.
        # Four-Foot Magic Bomb starts at 128, its subsequent upgrades are multiplied by percentage rounded up.
        # e.g. 20% of 128 = 25.6, meaning 128 + 25.6 = 153.6, rounded up = 154
        # Miracle Mallet's unique stat only ever stays at 400 in the vanilla game.
        cheat_item_use_count = 15
        # The game displays up to 9 at most, but the actual count can go beyond that.

        # Write level.
        addrItemLevel = getPointerAddress(self.pm, self.pm.base_address + 0xE6B9C, [
            ((cheat_item_id + 0x48f) * 0x34) + 0x1c
        ])
        addrItemStat = getPointerAddress(self.pm, self.pm.base_address + 0xE6B9C, [
            ((cheat_item_id + 0x48f) * 0x34) + 0x28
        ])
        addrItemCount = getPointerAddress(self.pm, self.pm.base_address + 0xE6B9C, [
            ((cheat_item_id + 0x48f) * 0x34) + 0x24
        ])

        self.pm.write_int(addrItemLevel, cheat_item_level)
        self.pm.write_int(addrItemStat, cheat_item_unique_stat)
        self.pm.write_int(addrItemCount, cheat_item_use_count)