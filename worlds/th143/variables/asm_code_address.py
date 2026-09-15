# ASM addresses for ASM hacks.
# All of these are static addresses that should be added onto the base address.
# These require no offsets at all, or only additions instead of proper pointer offsets.

# Addresses to disable forced item upgrades. Set to EB (1 byte).
ADDR_STATIC_ITEM_UPGRADES = (
    # Nimble Fabric
    0x566e4, 0x566fe, 0x56718, 0x56732, 0x5674c, 0x56766,
    # Tengu's Toy Camera
    0x56803, 0x5681d, 0x56837, 0x56851, 0x5686b, 0x56885,
    # Gap Folding Umbrella
    0x56916, 0x56930, 0x5694a, 0x56964, 0x5697e,
    # Ghastly Send-Off Lantern
    0x56a08, 0x56a22, 0x56a3c, 0x56a56,
    # Bloodthirsty Yin-yang Orb
    0x56aed, 0x56b07, 0x56b21,
    # Four-Foot Magic Bomb
    0x56bb2, 0x56bcc, 0x56be6, 0x56c00, 0x56c1a,
    # Substitute Jizo
    0x56cab, 0x56cc5, 0x56cdf, 0x56cf9, 0x56d13,
    # Cursed Decoy Doll
    0x56da1, 0x56dbb, 0x56dd5, 0x56def,
    # Miracle Mallet Replica
    0x56e85, 0x56e9f, 0x56eb9
)
ADDR_STATIC_MALLET_SUB4 = (
    # Miracle Mallet Sub-item's additions (part 1).
    # Set all to 0x90, length 4.
    0x5678f, 0x568ae, 0x569a7, 0x56a7f, 0x56b4a, 0x56c43
)
ADDR_STATIC_MALLET_SUB3 = (
    # Miracle Mallet Sub-item's additions (part 2).
    # Set all to 0x90, length 3.
    0x56d3c, 0x56e18, 0x56ee2
)
ADDR_STATIC_MAX_LEVEL = (
    # Overwrite with 0x90, length 7.
    0x566d6, 0x567f5, 0x56908, 0x569fa, 0x56ae4, 0x56ba4, 0x56c9d, 0x56d93, 0x56e7c
)

# Cheat code disabling.
# 18 bytes of 0x90 (NOP).
ADDR_STATIC_CHEAT_CODE = 0x65EED
# Change to 0x10 to play the invalid sound since the cheat code is disabled.
ADDR_STATIC_CHEAT_SOUND = 0x65EEC

# Disable saving replays if a scene was cleared successfully.
# Original opcodes are 7e, 0a. Change to 90, 90 to disable.
ADDR_STATIC_SAVE_REPLAY = 0x4AB90
# Change to anything but 0 to disable replays globally.
# Change back to 0 to enable.
ADDR_STATIC_CONTINUE_COUNT = 0xe4700
# Changing whether the Next Scene button actually takes you to the next scene.
# Originally 0x41 (increase by 1). Change to 0x00 to do nothing.
ADDR_STATIC_NEXT_SCENE = 0x4b1e5
# Disabling unlocking the next Day. Change to EB to always skip unlock.
ADDR_STATIC_UNLOCK_DAY = 0x62559

# Set playtime requirements for achievements.
# Written in little endian encoding/least significant byte first.
# 1 hour, 5 hours, and 10 hours, respectively. All 3 bytes.
ADDR_STATIC_PLAYTIME_REQ = [0x338AA, 0x338CE, 0x338F2]

# Disable special Scene 1 alerts. Change them to 0x90/NOP.
ADDR_STATIC_SCENE_ONE = [
    # 2 bytes
    (0x33d19, 0x33da6, 0x33e2f),
    # 5 bytes
    (0x33ce7, 0x33d6f, 0x33dfc, 0x33e50, 0x33e84),
    # 6 bytes
    (0x33d1b, 0x33d33, 0x33d39, 0x33d4a, 0x33d50, 0x33d61,
     0x33da8, 0x33dc0, 0x33dc6, 0x33dd7, 0x33ddd, 0x33dee, 0x33e42),
    # 7 bytes
    (0x33d21, 0x33dae, 0x33cec, 0x33d74, 0x33e01, 0x33e55, 0x33e89),
    # 11 bytes
    (0x33d28, 0x33d3f, 0x33d56, 0x33db5, 0x33dcc, 0x33de3, 0x33e37)
]

# Disable forcing equip of items during scenes.
# Override all with 0x90, length 10.
ADDR_STATIC_FORCE_ITEM = (0x6334e, 0x63358, 0x63388, 0x63392, 0x633c3, 0x633cd)
# Disable forced sub-item unlock during 6-1.
# Overwrite with 0x90, length 7.
ADDR_STATIC_FORCE_SUBITEM = 0x633bc
# If 6-1 is not cleared, the game will try to relock sub-items if they're unlocked.
# Overwrite with 0xEB to disable that.
ADDR_STATIC_LOCK_SUBITEM = 0x625d2


# Name of the BestShot folder.
# Change to 73 63 5F 31 34 33 61 70 (sc_143ap)
ADDR_STATIC_BESTSHOT_NAME = (0xc7ba0, 0xc5000)
# Name of the replay folder.
# Change to 72 65 70 5F 61 70 (rep_ap)
ADDR_STATIC_REPLAY_NAME = (0xc6ed8, 0xc7be4)
# Name of the scorefile.
# Change to 61 70 (scoreap143) upon connection.
ADDR_STATIC_SCOREFILE_NAME = 0xc7095

# Overwrite these with 0xEB
ADDR_STATIC_SCENE_LOCKS = (0x63a2d, 0x63a40, 0x63a53)
# Overwrite this with 0x90, 15 bytes.
ADDR_STATIC_DAY8_LOCK = 0x63a5f
# Overwrite how many scenes a day should have.
# The formula is (base address + the below + (day ID * 4))
# Day ID is 0-9. Each field is 4 bytes.
ADDR_STATIC_START_SCENE_COUNT = 0xc4a30