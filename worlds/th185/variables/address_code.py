ADDR_ANTICHEAT_HACK = 0x000744A6 # NOP opcodes should be used.
ADDR_ALERT_POPUP_PTR = 0x0004819F # Set this to 90, 90.
ADDR_ALERT_POPUP_FUNC = 0x000481A7 # Set this to 90, 90, 90, 90, 90.
ADDR_KOISHI_CARD_BUG = 0x0000E8C4 # Set this to 90, 90, 90, 90, 90.

# The original byte at these locations is 07.
# Overwrite with 0B (11). 12 is when the game crashes.
LIST_ADDR_LIVES_CAP = (
    # Function 1
    0x0a355,
    0x0a35b,
    0x0a36e,
    0x0a377,
    # Function 2 - Mokou's card
    0x0a43e,
    0x0a444,
    0x0a44b,
    0x0a451,
    0x0a460,
    0x0a46e,
    0x0a472,
    0x0a48c,
    0x0a495,
    # Function 3
    0x0aef8,
    0x0aeff,
    0x0af14,
    0x0af1d,
    # Function 4
    0x12e4c,
    0x12e52,
    0x12e65,
    0x12e6e,
    # Function 5 - Saki's Power card
    0x14d6c,
    0x14d72,
    0x14d85,
    0x14d8e
)

# Addresses of Card Upgrade conditional statements in the game's binary.
# Upgrades 1-4 require overwriting 3 bytes with 90 E9 BF.
# This skips the entire clause about setting card slots and equip cost.
# But it will not skip the entire upgrade section altogether.
ADDR_EQUIP_UPGRADE_1 = 0x0004A859
ADDR_EQUIP_UPGRADE_2 = 0x0004A953
ADDR_EQUIP_UPGRADE_3 = 0x0004AA4D
ADDR_EQUIP_UPGRADE_4 = 0x0004AB47
# Upgrade 5 is a 2-byte EB 1F.
ADDR_EQUIP_UPGRADE_5 = 0x0004AC41
# Upgrade 6 is a 1-byte 7E.
# The game checks if it's less than 7 cards here.
# However, it should be modified so that it only gives the achievement at 7 or more cards.
ADDR_EQUIP_UPGRADE_6 = 0x0004AC95
# Slot unlock and equip cost unlock specifically on the last upgrade should be deleted.
# 30 bytes in total. To simplify, overwrite from 4ac97 with a length of 30 with a bytearray of just 0x90.
# In a loop starting from 0, go up to 29 and then stop if >= 30.
ADDR_EQUIP_UPGRADE_7 = 0x0004AC97

ADDR_EQUIP_UPGRADE_SET = (ADDR_EQUIP_UPGRADE_1, ADDR_EQUIP_UPGRADE_2, ADDR_EQUIP_UPGRADE_3, ADDR_EQUIP_UPGRADE_4)

# Addresses of Card Upgrade conditional statements, checking for boss clears.
# These conditionals just skip the entire logic chain if the number of bosses defeated aren't met.
# This means it will also skip achievements.
# Disable that by making the number compared to always 0 instead, so that it always passes the checks.
ADDR_EQUIP_BOSS_CHECK_1 = 0x0004a833
ADDR_EQUIP_BOSS_CHECK_2 = 0x0004a921
ADDR_EQUIP_BOSS_CHECK_3 = 0x0004aa1b
ADDR_EQUIP_BOSS_CHECK_4 = 0x0004ab15
ADDR_EQUIP_BOSS_CHECK_5 = 0x0004ac0e
ADDR_EQUIP_BOSS_CHECK_6 = 0x0004ac65

ADDR_EQUIP_BOSS_SET = (ADDR_EQUIP_BOSS_CHECK_1, ADDR_EQUIP_BOSS_CHECK_2, ADDR_EQUIP_BOSS_CHECK_3, ADDR_EQUIP_BOSS_CHECK_4, ADDR_EQUIP_BOSS_CHECK_5, ADDR_EQUIP_BOSS_CHECK_6)

# This is mainly for menu cursor stuff. Override in order from 1-7.
# Address of the line that sets the cursor in the menu to Stage #.
ADDR_STAGE_CURSOR_STATIC = 0x000CDCAC # Set this when first loading into the game.
ADDR_CURSOR_SET_STAGE1 = 0x0004a3e8 + 6 # 1
ADDR_CURSOR_SET_STAGE2 = 0x0004a42a + 6 # 2
ADDR_CURSOR_SET_STAGE3 = 0x0004a4ae + 6 # 3
ADDR_CURSOR_SET_STAGE4 = 0x0004a532 + 6 # 4
ADDR_CURSOR_SET_STAGE5 = 0x0004a5b6 + 6 # 5
ADDR_CURSOR_SET_STAGE6 = 0x0004a64b + 6 # 6
ADDR_CURSOR_SET_CHIMATA = 0x0004a6cf + 6 # 7
ADDR_CURSOR_SET_CHALLENGE = 0x0004a73e + 6 # 7