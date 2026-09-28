# Various utils to get the names of things.
from .utils_math import clamp
from ..variables.game_info import AP_SAVE_DATA_FILE_NAME, JSON_EXTENSION
from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ..variables.location_item_name import CONST_ITEM_NAMES, \
	CONST_SPELLCARD_NAMES, CONST_NICKNAME_NAME, CONST_MUSIC_ROOM_NAMES, CONST_PROGRESSIVE_SCENE, \
	CONST_ITEM_STAT_NAMES, EVENT_ITEM_SCENE_CLEAR_NAME


#
# ITEMS
#
# Get Item names for things related to Cheat Items.
def get_item_name_level(item_id: int = 0) -> str:
	clean_item_num: int = clamp(item_id, 0, 8)
	item_name: str = CONST_ITEM_NAMES[clean_item_num]
	return f"Progressive {item_name}: Level Up"

def get_item_remove_cap(item_id: int = 0) -> str:
	clean_item_num: int = clamp(item_id, 0, 8)
	item_name: str = CONST_ITEM_NAMES[clean_item_num]
	return f"Progressive {item_name}: Remove Level Cap"

def get_item_name_usage(item_id: int = 0) -> str:
	clean_item_num: int = clamp(item_id, 0, 8)
	item_name: str = CONST_ITEM_NAMES[clean_item_num]
	return f"Progressive {item_name}: +1 Item Use Count"

def get_item_name_stat(item_id: int = 0) -> str:
	clean_item_num: int = clamp(item_id, 0, 8)
	item_name: str = CONST_ITEM_NAMES[clean_item_num]
	return f"Progressive {item_name}: {CONST_ITEM_STAT_NAMES[clean_item_num]} Up"

def get_item_name_subitem(item_id: int = 0) -> str:
	clean_item_num: int = clamp(item_id, 0, 8)
	item_name: str = CONST_ITEM_NAMES[clean_item_num]
	return f"{item_name} Sub-item"

# Day Number is indexed at 1.
def get_scene_unlock_name(day_number: int = 1) -> str:
	return f"Day {str(day_number)} {CONST_PROGRESSIVE_SCENE}"

def get_clear_with_item_fake(item_id: int = 0) -> str:
	return f"{EVENT_ITEM_SCENE_CLEAR_NAME} with {CONST_ITEM_NAMES[item_id]}"

#
# REGIONS
#
def get_entrance_to_region_name(new_region_str: str) -> str:
	return f"Menu to {new_region_str}"

#
# LOCATIONS - SCENES
#
# Day Number and Scene Number is indexed at 1.
# Example output: [Scene 1-1] Nonspell - Yatsuhashi Tsukumo
def get_location_name_scene(day_number: int = 1, scene_number: int = 1) -> str:
	clean_scene_num: int = clamp(scene_number - 1, 0, CONST_DAY_SCENE_COUNT[day_number - 1] - 1)
	return f"[Scene {str(day_number)}-{str(scene_number)}] {CONST_SPELLCARD_NAMES[day_number - 1][clean_scene_num]}"

# Day Number and Scene Number is indexed at 1.
# Example output: [Item Clear] Scene 1-1 Nimble Fabric
def get_location_name_scene_with_item(day_number: int = 1, scene_number: int = 1, item_id: int = 0) -> str:
	if item_id < 9:
		item_name = CONST_ITEM_NAMES[item_id]
	else:
		item_name = "No Items"
	return f"[Item Clear] Scene {str(day_number)}-{str(scene_number)} {item_name}"

#
# LOCATIONS - OTHER
#
# Nickname is indexed at 1.
def get_location_name_nickname(nickname_id: int = 1) -> str:
	clean_nickname_id: int = clamp(nickname_id - 1, 0, len(CONST_NICKNAME_NAME) - 1)
	return f"Nickname #{str(nickname_id)}: {CONST_NICKNAME_NAME[clean_nickname_id]}"

# Music Tracks are indexed at 1.
def get_location_name_music_room(music_id: int = 1) -> str:
	clean_music_room_id: int = clamp(music_id - 1, 0, len(CONST_MUSIC_ROOM_NAMES) - 1)
	return f"[Music Room] Track #{str(music_id)}: {CONST_MUSIC_ROOM_NAMES[clean_music_room_id]}"

#
# MISCELLANEOUS
#
# Save data stuff.
def get_item_index_save_name(seed_name, team_number, slot_number) -> str:
	return AP_SAVE_DATA_FILE_NAME + str(seed_name) + str(team_number) + str(slot_number) + JSON_EXTENSION