#
# Game scorefile pointer
#
# Can be used to check if the game is even open in the first place.
ADDR_BASE_SAVE_PTR = 0xe6b9c

# Notice/Alerts/Announcements
# 4-byte integer. Shows how many notices remain in queue.
OFFSET_NOTICE_QUEUE_COUNT = 0xf16c
# 1-byte.
# ((index of notice queue counter * 4) + 0xf170) = which notice to show at what index
OFFSET_NOTICE_QUEUE_INDEX = 0xf170
OFFSET_LAST_CHOSEN_DAY = 0xefa4
OFFSET_LAST_CHOSEN_SCENE = 0xefa8
OFFSET_LAST_MAIN_ITEM = 0xef9c
OFFSET_LAST_SUB_ITEM = 0xefa0
OFFSET_UNIQUE_SCENE_CLEARS = 0xef2c
OFFSET_SHOWN_CONGRATS_SCREEN = 0xefe0

# Achievements
# Add the corresponding Nickname index to this offset (+ operation, not another offset).
# Same with the Music Room.
OFFSET_NICKNAME = 0xeff9
OFFSET_MUSIC_ROOM = 0xef74

# Playtime (calculated at a value of 1sec:100frames)
# Mainly checks this one for achievements.
OFFSET_PLAYTIME_LOW = 0xEF94
# If this one is >0, instantly check the achievement.
OFFSET_PLAYTIME_HIGH = 0xEF98

# Death count
OFFSET_DEATH_COUNT = 0xF07C

# Days unlocked (0-9 for Day 1-10)
OFFSET_DAYS_UNLOCKED = 0xF084

# Vanilla Day unlocks
OFFSET_DAY_ONE_UNLOCK = 0xefb8
OFFSET_DAY_THREE_UNLOCK = 0xf088
OFFSET_DAY_FIVE_UNLOCK = 0xf089
OFFSET_DAY_SIX_UNLOCK = 0xf08a
OFFSET_DAY_EIGHT_UNLOCK = 0xf08b

#
# Items and Sub-items
#
# 0x0000 = 3 items
# 0x0100 or 0x0001 = 6 items
# 0x0002 or 0x0102 = 9/all items
OFFSET_ITEM_TIER_PROGRESS = 0xEFAC
OFFSET_SUB_ITEM_UNLOCK = 0xEFAD

# Items
def get_item_data_offset(item_id: int = 0):
	"""
	Retrieves the offset for item stats. Use this to + onto another offset number.
	This will return the results of `(main_item_id + 0x48f) * 0x34`. Add `0x1c` to get Level, for example.
	"""
	return (item_id + 0x48f) * 0x34

def get_item_level_offset(item_id: int = 0, is_level_cap: bool = False):
	"""
	This directly retrieves the offset for the item's Level stat address.
	Only the item level or the level cap. Not any other stat.
	"""
	if not is_level_cap:
		return (item_id * 0x34) + 0xed28
	else:
		return (item_id * 0x34) + 0xed2c

OFFSET_ITEM_LEVEL_NUM = 0x1c
OFFSET_ITEM_COUNT_NUM = 0x24
OFFSET_ITEM_STAT_NUM = 0x28

# Scene records
def get_item_clear_record_offset(absolute_scene_id: int = 1, item_id: int = 0):
	"""
	Returns the offset for whether an Item has been used to clear a specific Scene.
	Item ID is indexed from 0.
	If not 0, the item was used before.
	"""
	return ((item_id + 1) * 4) + (absolute_scene_id * 0x314) + 18

def get_scene_clear_offset(absolute_scene_id: int = 1):
	"""
	Returns the offset for Scene Clear count for specific scenes.
	If not 0, the Scene was cleared.
	"""
	return 0x40 + 0x314 * absolute_scene_id