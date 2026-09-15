# Other things related to game operation.
# Static address that only needs a + to base address.
ADDR_LAST_SCENE_CHOSEN = 0xe471c
ADDR_LAST_SCENE_CLEARED = 0xe6a2c
ADDR_LAST_DAY_CHOSEN = 0xE4734
ADDR_LAST_DAY_CHOSEN_MENU = 0xE4718

ADDR_SUB_ITEM_UNLOCK = 0xe4728
ADDR_CURRENT_SUB_ITEM = 0xE4714

# Main Menu Pointer
# To check for Scene Skip use, check for the following:
# - Last Scene Chosen is not 0 or FF.
# - Current Menu Chosen's first byte's left digit is 0 or 4.
# And just to be safe, upon coming back from a stage that finished viewing a replay,
# immediately set Last Scene Chosen to FF.
ADDR_BASE_MAIN_MENU = 0xe6bb4
OFFSET_CURRENT_MENU_CHOSEN = 0xe000

# Game tick.
ADDR_BASE_GAME_TICK = 0xe6a00
OFFSET_GAME_TICK = 0x4240
# Game Thread stuff. Returning 0 means not in stage, anything means in stage.
ADDR_BASE_GAME_THREAD = 0xE6A5C
# If this is not 0, a replay is currently being viewed.
OFFSET_GAME_IS_REPLAY = 0x94

# Held item pointer (in stage).
# Can also be used to check if the player is in a stage or not.
ADDR_BASE_HELD_ITEM = 0xE6B90
OFFSET_TOTAL_ITEMS_USED = 0x18
# offset 10 then offset 18
# => main item use count
# offset 18
# => how many times a main item has been used?
# offset 14 then offset 18
# -> sub item use count

# Player pointer
ADDR_BASE_PLAYER_POINTER = 0xe6b88
OFFSET_PLAYER_DEATH_STATE = 0x684
OFFSET_PLAYER_INVINC_STATE = 0x1847c

# Pause Menu pointer
ADDR_BASE_PAUSE_MENU = 0xE6A5C
OFFSET_IS_PAUSE_OPEN = 0x80