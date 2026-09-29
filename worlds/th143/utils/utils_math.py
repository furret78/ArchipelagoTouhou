import copy
import os

from Utils import user_path
from ..variables.game_info import CLIENT_DATA_PATH
from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT

def duplicate_list(original_list):
	return copy.deepcopy(original_list)

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Bit manipulation
def read_bit(bitarray: int = 0, index: int = 0) -> bool:
	"""
	If operation could not be done, return False.
	Index cannot go higher than 511 (512 bits).
	"""
	if index > 511: return False
	return (bitarray & 1 << index) != 0

def write_bit(bitarray: int = 0, index: int = 0, value: bool = False) -> int:
	"""
	If operation could not be carried out, return -1.
	Index cannot go higher than 511 (512 bits).
	"""
	if index > 511: return bitarray
	new_bitarray = bitarray
	if value:
		new_bitarray |= 1 << index
	else:
		new_bitarray &= ~(1 << index)
	return new_bitarray

def write_bit_savedata(data_int: int = 0, index: int = 0, value: bool = False) -> int:
	"""
	save_type 0 = Save Data A, anything else = B
	"""
	return write_bit(data_int, index, value)

def read_bit_savedata(data_int: int = 0, index: int = 0) -> bool:
	"""
	save_type 0 = Save Data A, anything else = B
	"""
	return read_bit(data_int, index)

def should_be_save_b(absolute_scene_id: int = 0) -> bool:
	return absolute_scene_id > 37

def get_scene_clear_neutral(save_data_ab: tuple[int, int], day_scene_id: tuple[int, int] = (1, 1), item_id: int = 0) -> bool:
	if not isinstance(save_data_ab[0], int) or not isinstance(save_data_ab[1], int):
		raise TypeError(f"Save data ints must be ints! SaveDataA: {str(save_data_ab[0])}, SaveDataB: {str(save_data_ab[1])}.")
	absolute_scene_id: int = get_absolute_scene_id(day_scene_id[0], day_scene_id[1]) - 1
	bit_position: int = get_bit_index_used(absolute_scene_id, item_id)
	if should_be_save_b(absolute_scene_id): # Use Save Data B.
		return read_bit_savedata(save_data_ab[1], bit_position)
	else: # Use Save Data A.
		return read_bit_savedata(save_data_ab[0], bit_position)

def set_scene_clear_neutral(save_data_ab: tuple[int, int], day_scene_id: tuple[int, int] = (1, 1), item_id: int = 0, value: bool = False) -> tuple[int, int]:
	absolute_scene_id: int = get_absolute_scene_id(day_scene_id[0], day_scene_id[1]) - 1
	bit_position: int = get_bit_index_used(absolute_scene_id, item_id)
	if should_be_save_b(absolute_scene_id):
		new_save_data = write_bit_savedata(save_data_ab[1], bit_position, value)
		return save_data_ab[0], new_save_data
	else:
		new_save_data = write_bit_savedata(save_data_ab[0], bit_position, value)
		return new_save_data, save_data_ab[1]

def get_bit_index_used(absolute_scene_id: int, item_id: int) -> int:
	# Absolute Scene ID passed in ideally should start from 0 and goes up to 74.
	clean_item_id: int = clamp(item_id, 0, 9)
	bit_position: int = (absolute_scene_id * 10) + clean_item_id
	if should_be_save_b(absolute_scene_id):
		bit_position = clamp(bit_position - (38 * 10), 0, 511)
	else:
		bit_position = clamp(bit_position, 0, 511)

	return bit_position

# Other
def get_relative_scene_id(absolute_scene_id: int = 1) -> tuple[int, int]:
	"""
	Returns the Day ID and Scene ID of this absolute scene ID in the form of a tuple.
	Day ID and Scene ID are both indexed from 1.
	"""
	relative_day_id: int = 1

	if 65 < absolute_scene_id <= 75: relative_day_id = 10
	elif 57 < absolute_scene_id <= 65: relative_day_id = 9
	elif 50 < absolute_scene_id <= 57: relative_day_id = 8
	elif 42 < absolute_scene_id <= 50: relative_day_id = 7
	elif 34 < absolute_scene_id <= 42: relative_day_id = 6
	elif 26 < absolute_scene_id <= 34: relative_day_id = 5
	elif 19 < absolute_scene_id <= 26: relative_day_id = 4
	elif 12 < absolute_scene_id <= 19: relative_day_id = 3
	elif 6 < absolute_scene_id <= 12: relative_day_id = 2

	relative_scene_id: int = clamp(absolute_scene_id, 1, 75)
	if relative_day_id > 1:
		for i in range(relative_day_id - 1):
			relative_scene_id -= CONST_DAY_SCENE_COUNT[i]

	return relative_day_id, relative_scene_id

def get_absolute_scene_id(day_id: int = 1, scene_id: int = 1) -> int:
	"""
	Day ID and Scene ID indexed from 1.
	Returns the absolute scene ID for a given Day and Scene within said Day.
	Absolute scene IDs are indexed from 1 to 75.
	"""
	clean_day_id: int = clamp(day_id, 1, 10)
	final_scene_id: int = clamp(scene_id, 1, CONST_DAY_SCENE_COUNT[clean_day_id - 1])
	if clean_day_id <= 1: return clamp(final_scene_id, 1, 6)
	for i in range(clean_day_id - 1):
		final_scene_id += CONST_DAY_SCENE_COUNT[i]
	return final_scene_id

def get_day_item_count(starting_day: int) -> int:
	"""
	How many Progressive Day items are remaining to unlock the rest of the Days.
	"""
	return clamp(9 - starting_day, 0, 9)

def get_pointer_address(pm, base, offsets):
	address = base
	for offset in offsets[:-1]:
		address = pm.read_uint(address)
		address += offset
	return pm.read_uint(address) + offsets[-1]

def client_directory_get_or_default():
	directory_path = user_path(CLIENT_DATA_PATH)
	if not os.path.exists(directory_path):
		os.makedirs(directory_path, exist_ok=True)