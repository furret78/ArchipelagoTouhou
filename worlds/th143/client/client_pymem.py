import pymem
import pymem.exception

from ..utils.utils_math import get_pointer_address, clamp
from ..variables.asm_code_address import *
from ..variables.game_data_address import *
from ..variables.game_info import FILE_NAME
from ..variables.game_save_address import *
from ..variables.game_stat_info import CONST_PLAYTIME_REQUIRE


class GameController:
	"""
	Class that directly mess with the game's memory.
	"""
	def __init__(self):
		self.pm = pymem.Pymem(process_name=FILE_NAME)

		# Scorefile (only valid if the game is running normally).
		self.ptrScorefile = self.pm.base_address + ADDR_BASE_SAVE_PTR
		# Held item in stage (only valid in stages).
		self.ptrHeldItem = self.pm.base_address + ADDR_BASE_HELD_ITEM
		self.ptrGameThread = self.pm.base_address + ADDR_BASE_GAME_THREAD
		self.ptrPlayer = self.pm.base_address + ADDR_BASE_PLAYER_POINTER
		self.ptrPauseMenu = self.pm.base_address + ADDR_BASE_PAUSE_MENU
		self.ptrGameTick = self.pm.base_address + ADDR_BASE_GAME_TICK

	#
	# Fundamental helper functions
	#
	def get_address_scorefile_base(self, offset):
		static_menu_base = self.pm.base_address + ADDR_BASE_SAVE_PTR
		return get_pointer_address(self.pm, static_menu_base, [offset])

	def get_address_custom_base(self, custom_base, offset):
		static_custom_base = self.pm.base_address + custom_base
		return get_pointer_address(self.pm, static_custom_base, [offset])

	def get_address_multiple_offset(self, custom_base, offset_list):
		static_custom_base = self.pm.base_address + custom_base
		return get_pointer_address(self.pm, static_custom_base, offset_list)

	#
	# Other utils
	#
	def is_game_running(self) -> bool:
		"""
		If True, the game is running and not the window resolution dialogue box.
		"""
		try:
			new_value = self.pm.read_int(self.ptrScorefile)
			if new_value <= 0: return False
		except Exception as e:
			return False

		return True


	def is_game_in_stage(self) -> bool:
		"""
		If True, the game is in a stage.
		"""
		return self.pm.read_int(self.ptrGameThread) != 0

	def is_game_paused(self) -> bool:
		"""
		If True, the game is in a stage AND currently paused.
		"""
		try:
			addrPauseMenu = self.get_address_custom_base(ADDR_BASE_PAUSE_MENU, OFFSET_IS_PAUSE_OPEN)
			return self.pm.read_short(addrPauseMenu) == 0x10
		except:
			return False

	def is_game_replay(self) -> bool:
		"""
		If True, the player is viewing a replay AND in a stage.
		"""
		addrIsReplay = self.get_address_custom_base(ADDR_BASE_GAME_THREAD, OFFSET_GAME_IS_REPLAY)
		return self.pm.read_short(addrIsReplay) != 0

	def is_game_scene_select(self) -> bool:
		"""
		If True, the player is currently in the scene select menu.
		May not be reliable if it's first boot-up
		"""
		addrIsSceneSelect = self.get_address_custom_base(ADDR_BASE_MAIN_MENU, OFFSET_CURRENT_MENU_CHOSEN)
		hex_byte_read = self.pm.read_bytes(addrIsSceneSelect, 1).hex()
		return hex_byte_read[0] == 0 or hex_byte_read[0] == 4

	def is_game_replay_select(self) -> bool:
		"""
		If True, the player is currently in the replay select menu.
		Last scene chosen value will not be cleared.
		"""
		addrIsReplaySelect = self.get_address_custom_base(ADDR_BASE_MAIN_MENU, OFFSET_CURRENT_MENU_CHOSEN)
		hex_byte_read = self.pm.read_bytes(addrIsReplaySelect, 1).hex()
		return hex_byte_read[1] == 8

	#
	# Initialization
	#
	# Overwriting specific parts of game code right as it boots up.
	# Initial Assembly hacks to make the AP function more independently.
	def init_game_asm_hacks(self):
		# Disable forced item upgrades.
		for static_addr in ADDR_STATIC_ITEM_UPGRADES:
			self.pm.write_bytes(self.pm.base_address + static_addr, bytes([0xEB]), 1)
		# Disable the Mallet's immediate stat boost effects.
		# The client can mimic this.
		for offset_4byte in ADDR_STATIC_MALLET_SUB4:
			self.pm.write_bytes(self.pm.base_address + offset_4byte, bytes([0x90, 0x90, 0x90, 0x90]), 4)
		for offset_3byte in ADDR_STATIC_MALLET_SUB3:
			self.pm.write_bytes(self.pm.base_address + offset_3byte, bytes([0x90, 0x90, 0x90]), 3)
		# Disable forced max level caps. That can be set later.
		for offset in ADDR_STATIC_MAX_LEVEL:
			self.pm.write_bytes(self.pm.base_address + offset, bytes([0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90]), 7)
		# Disable cheat code
		for i in range(18):
			self.pm.write_bytes(self.pm.base_address + ADDR_STATIC_CHEAT_CODE + i, bytes([0x90]), 1)
		self.pm.write_bytes(self.pm.base_address + ADDR_STATIC_CHEAT_SOUND, bytes([0x10]), 1)
		# Disable unlocking Next Day
		self.pm.write_bytes(self.pm.base_address + ADDR_STATIC_UNLOCK_DAY, bytes([0xEB]), 1)
		# Disable Scene 1 alerts
		for k in range(len(ADDR_STATIC_SCENE_ONE)):
			byte_length: int = 0
			match k:
				case 0: byte_length = 2
				case 1: byte_length = 5
				case 2: byte_length = 6
				case 3: byte_length = 7
				case 4: byte_length = 11

			for offset in ADDR_STATIC_SCENE_ONE[k]:
				for j in range(byte_length):
					self.pm.write_bytes(self.pm.base_address + offset + j, bytes([0x90]), 1)
		# Disable forcing item equips during certain scenes.
		for offset in ADDR_STATIC_FORCE_ITEM:
			self.pm.write_bytes(
				address=self.pm.base_address + offset,
				value=bytes([0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90]),
				length=10
			)
		# Disable forcing sub-item unlock during 6-1.
		self.pm.write_bytes(
			address=self.pm.base_address + ADDR_STATIC_FORCE_SUBITEM,
			value=bytes([0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90]),
			length=7
		)

		# Change various folder names
		# BestShot folder change to sc_143ap
		for offset in ADDR_STATIC_BESTSHOT_NAME:
			self.pm.write_bytes(
				address=self.pm.base_address + offset,
				value=bytes([0x73, 0x63, 0x5F, 0x31, 0x34, 0x33, 0x61, 0x70]),
				length=8
			)
		# Replay folder to rep_ap
		for offset in ADDR_STATIC_REPLAY_NAME:
			self.pm.write_bytes(
				address=self.pm.base_address + offset,
				value=bytes([0x72, 0x65, 0x70, 0x5F, 0x61, 0x70]),
				length=6
			)
		# Scorefile name to scoreap143.dat
		self.pm.write_bytes(self.pm.base_address + ADDR_STATIC_SCOREFILE_NAME, bytes([0x61, 0x70]), 2)

		# Override default scene locks
		for offset in ADDR_STATIC_SCENE_LOCKS:
			self.pm.write_bytes(
				address=self.pm.base_address + offset,
				value=bytes([0xEB]),
				length=1
			)
		for g in range(15):
			self.pm.write_bytes(
				address=self.pm.base_address + ADDR_STATIC_DAY8_LOCK + g,
				value=bytes([0x90]),
				length=1
			)

		previous_playtime = self.get_address_scorefile_base(OFFSET_PLAYTIME_HIGH)
		self.pm.write_int(previous_playtime, 0)

	def init_game_asm_playtime(self, playtime_mult: int):
		playtime_req_list = CONST_PLAYTIME_REQUIRE[clamp(playtime_mult, 0, 2)]
		for i in range(3):
			self.pm.write_bytes(
				address=self.pm.base_address + ADDR_STATIC_PLAYTIME_REQ[i],
				value=playtime_req_list[i],
				length=3
			)

	def set_day_scene_count(self, day_id: int, scene_count: int):
		safe_day_id: int = clamp(day_id, 0, 9)
		safe_scene_count: int = clamp(scene_count, 0, 10)
		self.pm.write_int(
			address=self.pm.base_address + ADDR_STATIC_START_SCENE_COUNT + (safe_day_id * 4),
			value=safe_scene_count
		)

	def set_main_item_tier(self, tier: int):
		addrMainItemTier = self.get_address_scorefile_base(OFFSET_ITEM_TIER_PROGRESS)
		self.pm.write_short(addrMainItemTier, tier)

	#
	# Player-specific functions
	#
	def get_player_state(self) -> bytes:
		addrPlayerState = self.get_address_custom_base(
			custom_base=ADDR_BASE_PLAYER_POINTER,
			offset=OFFSET_PLAYER_DEATH_STATE
		)
		return self.pm.read_bytes(addrPlayerState, 1)

	def set_player_state(self, player_state: bytes):
		addrPlayerState = self.get_address_custom_base(
			custom_base=ADDR_BASE_PLAYER_POINTER,
			offset=OFFSET_PLAYER_DEATH_STATE
		)
		self.pm.write_bytes(addrPlayerState, player_state, 1)

	def get_player_invinc(self) -> int:
		addrPlayerState = self.get_address_custom_base(
			custom_base=ADDR_BASE_PLAYER_POINTER,
			offset=OFFSET_PLAYER_INVINC_STATE
		)
		return self.pm.read_short(addrPlayerState)

	def set_player_invinc(self, invinc_code: int):
		addrPlayerState = self.get_address_custom_base(
			custom_base=ADDR_BASE_PLAYER_POINTER,
			offset=OFFSET_PLAYER_INVINC_STATE
		)
		self.pm.write_short(addrPlayerState, invinc_code)

	def get_stage_item_use(self) -> int:
		addrMainItemUse = self.get_address_multiple_offset(
			custom_base=ADDR_BASE_HELD_ITEM,
			offset_list=[0x10, 0x18]
		)
		return self.pm.read_int(addrMainItemUse)

	def set_stage_item_use(self, use_count: int):
		addrMainItemUse = self.get_address_multiple_offset(
			custom_base=ADDR_BASE_HELD_ITEM,
			offset_list=[0x10, 0x18]
		)
		self.pm.write_int(addrMainItemUse, clamp(use_count, 0, 99))

	def get_current_game_tick(self) -> int:
		addrCurrentGameTick = self.get_address_custom_base(ADDR_BASE_GAME_TICK, OFFSET_GAME_TICK)
		return self.pm.read_int(addrCurrentGameTick)

	#
	# Menu utilities
	#
	def get_last_day_chosen(self) -> int:
		return self.pm.read_int(self.pm.base_address + ADDR_LAST_DAY_CHOSEN)

	def get_last_scene_chosen(self) -> int:
		"""
		If this returns 0 or any values greater than 10, it is an invalid scene number.
		"""
		return self.pm.read_int(self.pm.base_address + ADDR_LAST_SCENE_CHOSEN)

	def get_notice_queue_count(self) -> int:
		addrNoticeCount = self.get_address_scorefile_base(OFFSET_NOTICE_QUEUE_COUNT)
		return self.pm.read_int(addrNoticeCount)

	def write_notice_queue_count(self, notice_count: int):
		clean_notice_count: int = clamp(notice_count, 0, 10)
		addrNoticeCount = self.get_address_scorefile_base(OFFSET_NOTICE_QUEUE_COUNT)
		self.pm.write_int(addrNoticeCount, clean_notice_count)

	def write_notice_into_game(self, notice_id: int, notice_index: int):
		clean_notice_index: int = clamp(notice_index, 0, 10)
		addrNoticeIndex = self.get_address_scorefile_base(
			offset=(OFFSET_NOTICE_QUEUE_INDEX + (clean_notice_index * 4))
		)
		self.pm.write_int(addrNoticeIndex, notice_id)

	def get_allclear_screen_shown(self) -> bool:
		congrats_addr = self.get_address_scorefile_base(OFFSET_SHOWN_CONGRATS_SCREEN)
		return self.pm.read_bool(
			address=congrats_addr
		)

	def set_allclear_screen_shown(self, screen_shown: bool):
		congrats_addr = self.get_address_scorefile_base(OFFSET_SHOWN_CONGRATS_SCREEN)
		self.pm.write_bool(
			address=congrats_addr,
			value=screen_shown
		)

	def toggle_next_scene_button(self, is_enabled: int):
		self.pm.write_bytes(
			address=self.pm.base_address + ADDR_STATIC_NEXT_SCENE,
			value=bytes([is_enabled]),
			length=1
		)

	def set_continues_used(self, number_used: int):
		self.pm.write_int(self.pm.base_address + ADDR_STATIC_CONTINUE_COUNT, number_used)

	def get_days_unlocked(self) -> int:
		"""Indexed from 0."""
		addrDaysUnlocked = self.get_address_scorefile_base(OFFSET_DAYS_UNLOCKED)
		return self.pm.read_int(addrDaysUnlocked)

	def set_days_unlocked(self, days_unlocked: int):
		"""Indexed from 0."""
		addrDaysUnlocked = self.get_address_scorefile_base(OFFSET_DAYS_UNLOCKED)
		self.pm.write_int(addrDaysUnlocked, days_unlocked)

	def get_death_count(self) -> int:
		addrDeathCount = self.get_address_scorefile_base(OFFSET_DEATH_COUNT)
		return self.pm.read_int(addrDeathCount)

	def set_death_count(self, death_count: int):
		addrDeathCount = self.get_address_scorefile_base(OFFSET_DEATH_COUNT)
		self.pm.write_int(addrDeathCount, death_count)

	def get_playtime(self) -> int:
		"""
		Returned result ratio: 1 second:100
		"""
		addrPlaytime = self.get_address_scorefile_base(OFFSET_PLAYTIME_LOW)
		return self.pm.read_int(addrPlaytime)

	def set_playtime(self, playtime: int):
		addrPlaytime = self.get_address_scorefile_base(OFFSET_PLAYTIME_LOW)
		self.pm.write_int(addrPlaytime, playtime)

	#
	# Records (Music Room + Nicknames)
	#
	def get_nickname_record(self, nickname_id: int) -> bool:
		"""
		Nickname ID is 0-69 (1-70).
		"""
		addrNicknameRecord = self.get_address_scorefile_base(OFFSET_NICKNAME + nickname_id)
		return self.pm.read_bool(addrNicknameRecord)

	def set_nickname_record(self, nickname_id: int, is_checked: bool):
		"""
		Nickname ID is 0-69 (1-70).
		"""
		addrNicknameRecord = self.get_address_scorefile_base(OFFSET_NICKNAME + nickname_id)
		self.pm.write_bool(addrNicknameRecord, is_checked)

	def get_music_record(self, music_id: int) -> bool:
		"""
		Music ID is 0-8 (1-9).
		"""
		addrMusicRecord = self.get_address_scorefile_base(OFFSET_MUSIC_ROOM + music_id)
		return self.pm.read_bool(addrMusicRecord)

	def set_music_record(self, music_id: int, is_checked: bool):
		"""
		Music ID is 0-8 (1-9).
		"""
		addrMusicRecord = self.get_address_scorefile_base(OFFSET_MUSIC_ROOM + music_id)
		self.pm.write_bool(addrMusicRecord, is_checked)

	#
	# Records (Generic Scene Clear Counts)
	#
	def get_scene_clear_generic(self, absolute_scene_id: int) -> int:
		addrSceneClear = self.get_address_scorefile_base(get_scene_clear_offset(absolute_scene_id))
		return self.pm.read_int(addrSceneClear)

	def set_scene_clear_generic(self, absolute_scene_id: int, clear_count: int):
		addrSceneClear = self.get_address_scorefile_base(get_scene_clear_offset(absolute_scene_id))
		self.pm.write_int(addrSceneClear, clear_count)

	def get_total_unique_clear(self) -> int:
		addrTotalUnique = self.get_address_scorefile_base(OFFSET_UNIQUE_SCENE_CLEARS)
		return self.pm.read_int(addrTotalUnique)

	def set_total_unique_clear(self, clear_count: int):
		addrTotalUnique = self.get_address_scorefile_base(OFFSET_UNIQUE_SCENE_CLEARS)
		self.pm.write_int(addrTotalUnique, clear_count)

	#
	# Records (Item-specific Scene Clear)
	#
	def get_scene_clear_item(self, absolute_scene_id: int, item_id: int) -> int:
		addrSceneClear = self.get_address_scorefile_base(get_item_clear_record_offset(absolute_scene_id, item_id))
		return self.pm.read_int(addrSceneClear)

	def set_scene_clear_item(self, absolute_scene_id: int, item_id: int, clear_count: int):
		addrSceneClear = self.get_address_scorefile_base(get_item_clear_record_offset(absolute_scene_id, item_id))
		self.pm.write_int(addrSceneClear, clear_count)

	#
	# Items
	#
	# Level
	def get_item_level(self, item_id: int) -> int:
		addrLevel = self.get_address_scorefile_base(get_item_level_offset(item_id) + OFFSET_ITEM_LEVEL_NUM)
		return self.pm.read_int(addrLevel)

	def set_item_level(self, item_id: int, level: int):
		addrLevel = self.get_address_scorefile_base(get_item_level_offset(item_id) + OFFSET_ITEM_LEVEL_NUM)
		self.pm.write_int(addrLevel, level)

	# Use count
	def get_item_use_count(self, item_id: int) -> int:
		addrUseCount = self.get_address_scorefile_base(get_item_data_offset(item_id) + OFFSET_ITEM_COUNT_NUM)
		return self.pm.read_int(addrUseCount)

	def set_item_use_count(self, item_id: int, count: int):
		addrUseCount = self.get_address_scorefile_base(get_item_data_offset(item_id) + OFFSET_ITEM_COUNT_NUM)
		self.pm.write_int(addrUseCount, count)

	# Unique stat
	def get_item_stat(self, item_id: int) -> int:
		addrUniqueStat = self.get_address_scorefile_base(get_item_data_offset(item_id) + OFFSET_ITEM_STAT_NUM)
		return self.pm.read_int(addrUniqueStat)

	def set_item_stat(self, item_id: int, stat_num: int):
		addrUniqueStat = self.get_address_scorefile_base(get_item_data_offset(item_id) + OFFSET_ITEM_STAT_NUM)
		self.pm.write_int(addrUniqueStat, stat_num)

	# Max level
	def get_item_max_level(self, item_id: int) -> int:
		addrMaxLevel = self.get_address_scorefile_base(get_item_level_offset(item_id, True))
		return self.pm.read_int(addrMaxLevel)

	def set_item_max_level(self, item_id: int, level_num: int):
		addrMaxLevel = self.get_address_scorefile_base(get_item_level_offset(item_id, True))
		self.pm.write_int(addrMaxLevel, level_num)

	#
	# Sub-items
	#
	def get_subitem_slot_unlock(self) -> bool:
		subitem_unlock = self.get_address_scorefile_base(OFFSET_SUB_ITEM_UNLOCK)
		return self.pm.read_bool(subitem_unlock)

	def set_subitem_slot_unlock(self, is_unlocked: bool):
		subitem_unlock = self.get_address_scorefile_base(OFFSET_SUB_ITEM_UNLOCK)
		self.pm.write_bool(
			address=subitem_unlock,
			value=is_unlocked
		)
		self.pm.write_bool(self.pm.base_address + ADDR_SUB_ITEM_UNLOCK, is_unlocked)

	def get_subitem_chosen(self) -> int:
		return self.pm.read_int(self.pm.base_address + ADDR_CURRENT_SUB_ITEM)

	def set_subitem_chosen(self, item_id: int):
		self.pm.write_int(self.pm.base_address + ADDR_CURRENT_SUB_ITEM, item_id)