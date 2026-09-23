from ..client.client_pymem import GameController
from ..utils.utils_math import get_absolute_scene_id, clamp
from ..variables.game_notice_id import CONST_NOTICE_ITEM_ID
from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT, CONST_ITEM_UPGRADE_STAT
from ..variables.location_item_name import CONST_NICKNAME_NAME
from ..worldgen.items import get_vanilla_level_max, get_vanilla_count_unique, get_vanilla_stat_unique

TOTAL_NICKNAME_COUNT = len(CONST_NICKNAME_NAME)

class GameHandler:
	"""
	Class that keeps track of some game data.
	"""
	previous_location_checked: list = []
	item_stats: list[dict[str, int]] = []
	nickname_data: int = 0
	music_data: list[bool] = []
	days_unlocked: int = 0
	scenes_unlocked: list[int] = []
	notice_queue: list[int] = []
	is_executing_notice: bool = False
	treasure_count: int = 0
	treasure_minimum: int = 1
	options = None
	subitem_slot_unlocked: bool = False
	subitems_unlocked: list[bool] = []
	can_add_notice: bool = False

	def __init__(self):
		self.gameController = GameController()
		self.reset()
		self.init_game()

	def reconnect(self):
		self.gameController = GameController()
		self.init_game()

	def reset(self):
		"""
		Initialize everything to defaults.
		"""
		self.item_stats = [
			# Nimble Fabric
			{
				"level": 0, # The level count.
				"count": 0, # The Use Count upgrade count, not use count itself.
				"stat": 0, # The stat upgrade count, not the stat itself.
				"capped": True
			},
			# Tengu's Toy Camera
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Gap Folding Umbrella
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Ghastly Send-Off Lantern
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Bloodthirsty Yin-yang Orb
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Four-Foot Magic Bomb
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Substitute Jizo
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Cursed Decoy Doll
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			},
			# Miracle Mallet (Replica)
			{
				"level": 0,
				"count": 0,
				"stat": 0,
				"capped": True
			}
		]
		self.nickname_data = 0
		self.music_data = [
			False, False, False, False, False, False, False, False, False
		]
		self.days_unlocked = 0
		self.scenes_unlocked = [
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		]
		self.notice_queue = []
		self.is_executing_notice = False
		self.treasure_count = 0
		self.treasure_minimum = 1
		self.subitem_slot_unlocked = False
		self.subitems_unlocked = [
			False, False, False, False, False, False, False, False
		]
		self.can_add_notice = False

	def init_game(self):
		if self.gameController is None: return
		self.gameController.init_game_asm_hacks()
		self.gameController.set_main_item_tier(0x0102)

	def init_game_set_playtime(self, playtime_mult: int):
		self.gameController.init_game_asm_playtime(playtime_mult)

	#
	# Stage Utils
	#
	def is_game_running(self) -> bool:
		if self.gameController is None: return False
		return self.gameController.is_game_running()

	def is_game_in_stage(self) -> bool:
		return self.gameController.is_game_in_stage()

	def is_game_paused(self) -> bool:
		return self.gameController.is_game_paused()

	def is_game_replay(self) -> bool:
		return self.gameController.is_game_replay()

	#
	# Player Utils
	#
	def check_player_death(self) -> bool:
		bytes_read = self.gameController.get_player_state()
		return bytes_read == bytes([0x02]) or bytes_read == bytes([0x04])

	def check_player_normal(self) -> bool:
		bytes_read = self.gameController.get_player_state()
		return bytes_read == bytes([0x01])

	def kill_player(self):
		self.gameController.set_player_state(bytes([0x04]))

	def check_player_invincibility(self) -> bool:
		int_read = self.gameController.get_player_invinc()
		return int_read in (0x20, 0x32, 0xA0)

	def remove_player_invincibility(self, old_conditional: int = 0x00):
		if old_conditional != 0x00:
			if self.gameController.get_player_invinc() != old_conditional: return

		self.gameController.set_player_invinc(0x400)

	def add_stage_main_item_use(self, use_count: int = 0):
		old_value = self.gameController.get_stage_item_use()
		self.gameController.set_stage_item_use(old_value + use_count)

	def add_playtime(self, playtime_sec: int):
		playtime_converted = playtime_sec * 100
		old_value = self.gameController.get_playtime()
		self.gameController.set_playtime(old_value + playtime_converted)

	def add_death_count(self, death_count: int):
		old_value = self.gameController.get_death_count()
		self.gameController.set_death_count(old_value + death_count)

	def set_freeze_trap(self):
		self.gameController.set_player_invinc(0x10)

	def remove_freeze_trap(self):
		old_value = self.gameController.get_player_invinc()
		if old_value == 0x10:
			self.gameController.set_player_invinc(0x400)

	#
	# Stage-specific Utils
	#
	def is_stage_reset(self) -> bool:
		return self.gameController.get_current_game_tick() < 30

	def get_current_day_and_scene(self):
		return self.gameController.get_last_day_chosen(), self.gameController.get_last_scene_chosen()

	#
	# Notice Utils
	#
	def add_notice_to_queue(self, notice_id: int):
		if not self.can_add_notice: return
		if notice_id <= 0: return
		if notice_id in (22, 23, 24, 28, 29): return
		if notice_id > 39: return

		self.notice_queue.append(notice_id)
		return

	def execute_notice(self):
		notice_queue_length = len(self.notice_queue)
		if notice_queue_length <= 0: return

		current_notice_count = self.gameController.get_notice_queue_count()
		if current_notice_count <= 0 and self.is_executing_notice:
			self.is_executing_notice = False
			return
		if current_notice_count > 0 or self.is_executing_notice: return
		self.is_executing_notice = True

		total_notice_count = clamp(notice_queue_length, 0, 10)
		for notice_index in range(total_notice_count):
			self.gameController.write_notice_into_game(self.notice_queue[notice_index], notice_index)

		if total_notice_count < notice_queue_length:
			self.notice_queue = self.notice_queue[total_notice_count:]
		else: self.notice_queue.clear()

		self.gameController.write_notice_queue_count(total_notice_count)
		return

	def add_notice_item(self, item_id: int = 0, upgrade_type: int = 0):
		"""
		Function that adds notices according to item upgrades.

		0 - Item unlocks.
		1 - Use count upgrade (Some items never get count upgrades in vanilla, will reuse 0).
		2 - Unique stat upgrade (Yin-yang Orb has no unique stat upgrade, will reuse 0).
		"""
		clean_item_id: int = clamp(item_id, 0, 8)
		clean_notice_type: int = clamp(upgrade_type, 0, 2)

		result_notice_id: int = CONST_NOTICE_ITEM_ID[clean_item_id][clean_notice_type]
		if clean_notice_type <= 0 and result_notice_id == CONST_NOTICE_ITEM_ID[clean_item_id][0]: return

		self.add_notice_to_queue(result_notice_id)
		return

	def add_notice_day_unlock(self, day_id: int = 1):
		"""
		Function that adds notices according to Day unlocked. Day 2-10, indexed from 1.
		"""
		clean_day_id: int = clamp(day_id - 2, 0, 8)
		result_notice_id: int = 30 + clean_day_id

		self.add_notice_to_queue(result_notice_id)
		return

	def add_notice_congrats(self):
		self.add_notice_to_queue(39)

	#
	# Records Utils: Scenes
	#
	# Retrieval from in-game data.
	def get_scene_generic_clear(self, day_and_scene_id: tuple[int, int] = (1, 1)) -> bool:
		absolute_scene_id: int = get_absolute_scene_id(day_and_scene_id[0], day_and_scene_id[1])
		return self.gameController.get_scene_clear_generic(absolute_scene_id) > 0

	def set_scene_generic_clear(self, day_and_scene_id: tuple[int, int] = (1, 1), value: bool = False):
		final_value: int = 0
		if value:
			if self.get_scene_generic_clear(day_and_scene_id): return
			final_value = 1
		absolute_scene_id: int = get_absolute_scene_id(day_and_scene_id[0], day_and_scene_id[1])
		self.gameController.set_scene_clear_generic(absolute_scene_id, final_value)

	def get_scene_item_clear(self, day_and_scene_id: tuple[int, int] = (1, 1), item_id: int = 0) -> bool:
		clean_item_id: int = clamp(item_id, 0, 9)
		absolute_scene_id: int = get_absolute_scene_id(day_and_scene_id[0], day_and_scene_id[1])
		return self.gameController.get_scene_clear_item(absolute_scene_id, clean_item_id) > 0

	def set_scene_item_clear(self, day_and_scene_id: tuple[int, int] = (1, 1), item_id: int = 0, value: bool = False):
		final_value: int = 0
		if value:
			if self.get_scene_item_clear(day_and_scene_id, item_id): return
			final_value = 1
		clean_item_id: int = clamp(item_id, 0, 9)
		absolute_scene_id: int = get_absolute_scene_id(day_and_scene_id[0], day_and_scene_id[1])
		self.gameController.set_scene_clear_item(absolute_scene_id, clean_item_id, final_value)

	# Other Utils
	def do_scene_skip(self, day_and_scene_id: tuple[int, int] = (1, 1)):
		self.set_scene_generic_clear(day_and_scene_id, True)
		for i in range(10):
			self.set_scene_item_clear(day_and_scene_id, i, True)

	def toggle_next_scene_button(self, value: bool):
		final_value: int = 0x41
		if not value: final_value = 0x00
		self.gameController.toggle_next_scene_button(final_value)

	def toggle_saving_replays(self, value: bool):
		final_value: int = 1
		if not value: final_value = 0
		self.gameController.set_continues_used(final_value)

	def add_days_unlocked(self):
		self.days_unlocked = clamp(self.days_unlocked + 1, 0, 9)

	def set_scene_unlock(self, day_id: int = 1, scene_count: int = 0):
		clean_day_id: int = clamp(day_id - 1, 0, 9)
		clean_scene_count: int = clamp(scene_count, 0, CONST_DAY_SCENE_COUNT[clean_day_id])
		self.gameController.set_day_scene_count(clean_day_id, clean_scene_count)

	def get_day_clear_count(self, day_id: int = 1) -> int:
		"""
		Retrieves the number of cleared Scenes in the specified Day.
		"""
		clear_count: int = 0
		for scene_id in CONST_DAY_SCENE_COUNT[day_id - 1]:
			if self.get_scene_generic_clear((day_id, scene_id + 1)):
				clear_count += 1
		return clear_count

	def get_all_days_clear_minimum(self, minimum_clear_per_day: int = 1) -> bool:
		"""
		Checks each day for a minimum count of scene clears.
		"""
		for day_id in range(10):
			if self.get_day_clear_count(day_id + 1) < minimum_clear_per_day: return False

		return True

	def get_all_days_all_clear(self) -> bool:
		"""
		Checks for all "Day Master" nicknames.
		"""
		for nickname_id in range(10):
			if not self.get_nickname_check(nickname_id + 20): return False

		return True

	def get_all_nicknames_check(self, include_hidden: bool = False) -> bool:
		for i in range(TOTAL_NICKNAME_COUNT):
			if not include_hidden and i >= (TOTAL_NICKNAME_COUNT - 10): continue
			if not self.get_nickname_check(i): return False

		return True

	def get_treasure_condition(self) -> bool:
		return self.treasure_count >= self.treasure_minimum

	#
	# Records Utils: Nicknames and Music Room
	#
	def get_nickname_check(self, nickname_id: int = 0) -> bool:
		clean_nickname_id: int = clamp(nickname_id, 0, 69)
		return self.gameController.get_nickname_record(clean_nickname_id)

	def set_nickname_check(self, nickname_id: int = 0, is_checked: bool = False):
		clean_nickname_id: int = clamp(nickname_id, 0, 69)
		self.gameController.set_nickname_record(clean_nickname_id, is_checked)

	def get_music_check(self, music_id: int = 0) -> bool:
		clean_music_id: int = clamp(music_id, 0, 8)
		return self.gameController.get_music_record(clean_music_id)

	def set_music_check(self, music_id: int = 0, is_checked: bool = False):
		clean_music_id: int = clamp(music_id, 0, 8)
		self.gameController.set_music_record(clean_music_id, is_checked)

	#
	# Cheat Items
	#
	def check_current_subitem(self) -> int:
		return self.gameController.get_subitem_chosen()

	def force_lock_subitem_individual(self):
		self.gameController.set_subitem_chosen(9)

	def is_subitem_unlocked(self) -> bool:
		return self.gameController.get_subitem_slot_unlock()

	def set_subitem_unlock(self, is_unlocked: bool = False):
		self.gameController.set_subitem_slot_unlock(is_unlocked)

	def get_item_data(self, item_id: int, data_type: int = -1) -> int:
		clean_item_id: int = clamp(item_id, 0, 8)
		match data_type:
			case 0: # Level
				return self.gameController.get_item_level(clean_item_id)
			case 1: # Count
				return self.gameController.get_item_use_count(clean_item_id)
			case 2: # Unique Stat
				return self.gameController.get_item_stat(clean_item_id)
			case _: # Max Level
				return self.gameController.get_item_max_level(clean_item_id)

	def set_item_data(self, item_id: int, value: int, data_type: int = -1):
		clean_item_id: int = clamp(item_id, 0, 8)
		match data_type:
			case 0: # Level
				self.gameController.set_item_level(clean_item_id, value)
			case 1: # Count
				self.gameController.set_item_use_count(clean_item_id, value)
			case 2: # Unique Stat
				self.gameController.set_item_stat(clean_item_id, value)
			case _: # Max Level
				self.gameController.set_item_max_level(clean_item_id, value)

	def set_default_item_data(self):
		for i in range(9):
			# Set all used item data
			for k in range(3):
				self.set_item_data(item_id=i, value=0, data_type=k)
				self.item_stats[i]["capped"] = True
			# Set max level
			self.set_item_data(item_id=i, value=get_vanilla_level_max(i), data_type=-1)

	def set_day_all_scenes(self, day_id: int = 0):
		"""
		Function that unlocks all Scenes within a specific Day.
		"""
		self.scenes_unlocked[day_id] = CONST_DAY_SCENE_COUNT[day_id]

	def set_all_days_full_unlock(self):
		"""
		Function that unlocks all Scenes in all Days.
		"""
		for i in range(9):
			self.scenes_unlocked[i] = CONST_DAY_SCENE_COUNT[i]
		self.update_day_and_scenes()

	#
	# Generic game status updates
	#
	def update_day_and_scenes(self):
		# Clamp day unlock count.
		self.days_unlocked = clamp(self.days_unlocked, 0, 9)
		self.gameController.set_days_unlocked(self.days_unlocked)
		# Clamp scenes count.
		for day_id in range(10):
			self.scenes_unlocked[day_id] = clamp(self.scenes_unlocked[day_id], 0, CONST_DAY_SCENE_COUNT[day_id])
			self.gameController.set_day_scene_count(
				day_id=day_id,
				scene_count=self.scenes_unlocked[day_id] or 0
			)
		return

	def update_cheat_items(self, is_level_based: bool = True):
		# TODO: Add a branch for dealing with custom upgrades.
		if is_level_based:
			for item_id in range(9):
				# TODO: Figure out a case for Max+ upgrades.
				clean_level_num: int = clamp(
					n=self.item_stats[item_id]["level"],
					smallest=0,
					largest=get_vanilla_level_max(item_id)
				)
				if clean_level_num < 0: continue
				self.gameController.set_item_level(item_id, clean_level_num)
				self.gameController.set_item_use_count(item_id, CONST_ITEM_UPGRADE_STAT[item_id]["count"][clean_level_num - 1])
				self.gameController.set_item_stat(item_id, CONST_ITEM_UPGRADE_STAT[item_id]["stat"][clean_level_num - 1])
		else:
			for item_id in range(9):
				CONST_USE_COUNT_LIST = get_vanilla_count_unique(item_id)
				clean_use_count: int = clamp(
					n=self.item_stats[item_id]["count"],
					smallest=0,
					largest=len(CONST_USE_COUNT_LIST)
				)
				if clean_use_count > 0:
					self.gameController.set_item_use_count(item_id, CONST_USE_COUNT_LIST[clean_use_count - 1])

				CONST_STAT_LIST = get_vanilla_stat_unique(item_id)
				clean_stat_count: int = clamp(
					n=self.item_stats[item_id]["stat"],
					smallest=0,
					largest=len(CONST_STAT_LIST)
				)
				if clean_stat_count > 0:
					self.gameController.set_item_stat(item_id, CONST_STAT_LIST[clean_stat_count - 1])

				if self.item_stats[item_id]["level"] < 0: self.item_stats[item_id]["level"] = 0
				self.gameController.set_item_level(item_id, self.item_stats[item_id]["level"])
		return

	def update_sub_items(self, subitem_list):
		if not self.options["subitem_individual"]:
			self.subitems_unlocked = [
				True, True, True, True, True, True, True, True
			]

		# Check for the Sub-item slot unlock.
		self.gameController.set_subitem_slot_unlock(self.subitem_slot_unlocked)

		# Check for each individual item.
		if len(subitem_list) <= 0: return

		for sub_id in subitem_list:
			self.subitems_unlocked[clamp(sub_id - 51, 0, 8)] = True

		self.correct_sub_item()
		return

	def correct_sub_item(self):
		current_chosen_sub = self.gameController.get_subitem_chosen()
		if not self.subitems_unlocked[current_chosen_sub]: self.force_lock_subitem_individual()