import unittest

import pymem

from ..Tools import getPointerAddress, get_internal_boss_id_to_client
from ..variables.address_card_dex import ADDR_DEX_NO_CARD
from ..variables.address_code import LIST_ADDR_LIVES_CAP, ADDR_KOISHI_CARD_BUG, ADDR_ANTICHEAT_HACK
from ..variables.address_gameplay import ADDR_LAST_BOSS_MET, ADDR_CURRENT_STAGE_PTR, ADDR_SHOT_ATTACK
from ..variables.card_const import ADDR_CARD_TO_DEX, MALLET_CARD, SAKI_BIGSHOT_CARD, SAKI_POWER_CARD
from ..variables.meta_data import DISPLAY_NAME
from .. import TouhouHBMWorld, FILE_NAME, ADDR_BASE_MENU_PTR, ADDR_STAGE_ID_TO_PTR, ADDR_EQUIP_COST


class PythonTestFunctions(unittest.TestCase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def test_read_mallet_bytes(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, [ADDR_CARD_TO_DEX[MALLET_CARD]])
        print(self.pm.read_bytes(addrFromCardDex, 1))

    def test_write_mallet_bytes(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR,
                                            [ADDR_CARD_TO_DEX[MALLET_CARD]])
        self.pm.write_bytes(addrFromCardDex, bytes([0x00]), 1)
        print(self.pm.read_bytes(addrFromCardDex, 1))

    def test_read_boss_data(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrBossMet = self.pm.base_address + ADDR_LAST_BOSS_MET
        last_boss_met_id = self.pm.read_int(addrBossMet)
        if last_boss_met_id < 1 or last_boss_met_id > 28: last_boss_met_id = -1
        print(f"Boss Met: {get_internal_boss_id_to_client(last_boss_met_id)}")

    def test_read_stage_status(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrStageStatus = self.pm.base_address + ADDR_CURRENT_STAGE_PTR
        addrUsed = getPointerAddress(self.pm, addrStageStatus, [0xB0])
        print(f"Stage status: {self.pm.read_int(addrUsed)}")

    def test_read_shot_attack(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrShotAttack = self.pm.base_address + ADDR_SHOT_ATTACK
        #addrUsed = getPointerAddress(self.pm, addrStageStatus, [0xB0])
        print(f"Shot Attack%: {self.pm.read_short(addrShotAttack)}")

    def test_write_shot_attack(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrShotAttack = self.pm.base_address + ADDR_SHOT_ATTACK
        self.pm.write_short(addrShotAttack, 1000)
        print(f"Shot Attack%: {self.pm.read_short(addrShotAttack)}")

    def test_unlock_blank_slot(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrNoCard = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, [ADDR_DEX_NO_CARD])
        self.pm.write_bytes(addrNoCard, bytes([0x01]), 1)

    def test_increase_lives_cap(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        for addr in LIST_ADDR_LIVES_CAP:
            addrLifeCapNum = self.pm.base_address + addr
            self.pm.write_bytes(addrLifeCapNum, bytes([0x0B]), 1)

    def test_disable_anticheat(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.pm.write_bytes(self.pm.base_address + ADDR_ANTICHEAT_HACK, bytes([0x90, 0x90]), 2)

    def test_unlock_stage(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        STAGE_NUM = 1
        IS_UNLOCKED_BOOL = True
        STAGE_ADDRESS = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, [ADDR_STAGE_ID_TO_PTR[STAGE_NUM]])
        self.pm.write_bool(STAGE_ADDRESS, IS_UNLOCKED_BOOL)

    def test_unlock_card(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        CARD_STRING_ID = SAKI_POWER_CARD
        IS_UNLOCKED_BOOL = True
        CARD_ADDRESS = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR,
                                          [ADDR_CARD_TO_DEX[CARD_STRING_ID]])
        self.pm.write_bool(CARD_ADDRESS, IS_UNLOCKED_BOOL)

    def test_set_equip_cost(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        EQUIP_COST_AMOUNT = 500
        EQUIP_COST_ADDRESS = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR,
                                          [ADDR_EQUIP_COST])
        self.pm.write_int(EQUIP_COST_ADDRESS, EQUIP_COST_AMOUNT)

    def test_lives_cap(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        LIST_ADDR_LIVES_CAP = (
            0x14d6c,
            0x14d72,
            0x14d85,
            0x14d8e
        )
        for offset in LIST_ADDR_LIVES_CAP:
            self.pm.write_bytes(self.pm.base_address + offset, bytes([0x07]), 1)