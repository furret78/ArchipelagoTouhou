import asyncio
import unittest

import pymem

from BaseClasses import MultiWorld
from ..utils.utils_math import get_absolute_scene_id, get_relative_scene_id, get_pointer_address
from ..variables.game_info import FILE_NAME


def getPointerAddress(pm, base, offsets):
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset
    return pm.read_uint(address) + offsets[-1]

class ISCStatTest(unittest.TestCase):
    multiworld: MultiWorld

    def test_write_bit(self):
        test_bit_array = 0b0000
        test_bit_array |= 1 << 3
        print(bin(test_bit_array)) # Written right to left, indexed at 0.

    def test_read_bit(self):
        test_bit_array = 0b1101
        print(test_bit_array & 1 << 1 != 0) # Read right to left, indexed at 0.

    def test_get_absolute_scene_id(self):
        print(get_absolute_scene_id(6, 7))

    def test_get_relative_scene_id(self):
        day_id, scene_id = get_relative_scene_id(41)
        print(f"Day ID: {day_id}, Scene ID: {scene_id}")

    def test_read_left_digit_hex(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrMenu = get_pointer_address(self.pm, self.pm.base_address + 0xe6bb4, [0xe000])
        hex_byte_read = self.pm.read_bytes(addrMenu, 1).hex()
        print(hex_byte_read[0])
        # This gets the left digit of a hex byte. Change to [1] to read the right side.