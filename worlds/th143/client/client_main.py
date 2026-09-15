import asyncio

import Utils
import colorama
import os
import orjson
import traceback

from typing import Optional, Any

from CommonClient import (
	CommonContext,
	get_base_parser,
	logger,
	server_loop,
	gui_enabled,
)
from NetUtils import NetworkItem
from Utils import user_path
from .client_handler import GameHandler
from ..utils.utils_get_name import get_item_index_save_name, get_location_name_nickname, get_location_name_music_room, \
	get_location_name_scene, get_location_name_scene_with_item
from ..utils.utils_math import client_directory_get_or_default, set_scene_clear_neutral, get_scene_clear_neutral, \
	should_be_save_b, clamp
from ..variables.game_info import DISPLAY_NAME, SHORT_NAME, CLIENT_DATA_PATH, JSON_SLOT_ITEMS, JSON_SLOT_NAME, \
	JSON_SLOT_CLEARS_A, JSON_SLOT_CLEARS_B, JSON_SLOT_PLAYTIME, JSON_SLOT_DEATHS, JSON_SLOT_SCENE_SKIP
from ..client.client_cmd import CommandProccessorISC
from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT, CONST_MAX_PLAYTIME_CLIENT, CONST_MAX_DEATHS_CLIENT, \
	CONST_MAX_SCENE_SKIPS
from ..variables.location_item_name import CONST_NICKNAME_NAME, CONST_ITEM_SHORT_TO_ID, CONST_PROGRESSIVE_DAY, \
	CONST_SUBITEM_SLOT_NAME
from ..worldgen.items import item_table
from ..worldgen.world_locations.location_table import location_table

CONST_TOTAL_NICKNAME_COUNT = len(CONST_NICKNAME_NAME)
CONST_TOTAL_ITEM_COUNT = len(CONST_ITEM_SHORT_TO_ID.keys())

class ContextISC(CommonContext):
	"""Touhou 14.3 Game Context"""
	# Game Handler
	handler: GameHandler = None

	def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
		super().__init__(server_address, password)
		self.item_ap_id_to_name = None
		self.item_name_to_ap_id = None
		self.location_ap_id_to_name = None
		self.options = None
		self.is_connected = None
		self.in_error = None
		self.location_name_to_ap_id = None
		self.all_location_ids = []
		self.previous_location_checked = []
		self.game = DISPLAY_NAME
		self.items_handling = 0b111  # Item from starting inventory, own world and other world
		self.command_processor = CommandProccessorISC
		self.last_received_item_index_server: int = -1

		self.retrieved_custom_data: bool = False
		self.loaded_past_received_items: bool = False
		self.all_received_items = None
		self.client_settings = {}

		# Scene Clear data is split into 2 integers, modified with bit-shifting.
		# DataStorage only allows up to 512 bits/64 bytes per integer.
		# We have 750 booleans representing 75 scenes x 10 items (including itemless).
		# We should be using absolute_scene_id very often.
		# The first 500 bits (indexed 0-499) are used up by Day 1-7. This goes in Scene Clears A.
		# The last 250 (indexed 0-249) used by Day 8-10 goes in Scene Clears B.

		# If all locations for Item-specific Scene Clears are enabled, use locations checked instead of DataStorage.
		self.custom_data_keys_list: list = [str(self.team) + "_" + str(self.slot) + "SaveA143", # Scene Clears A
											str(self.team) + "_" + str(self.slot) + "SaveB143", # Scene Clears B
											str(self.team) + "_" + str(self.slot) + "Playtime143",
											str(self.team) + "_" + str(self.slot) + "Deaths143",
											str(self.team) + "_" + str(self.slot) + "Skips143"]

		# Save data
		self.save_data_a: int = 0x0
		self.save_data_b: int = 0x0
		self.save_playtime: int = 0
		self.save_deaths: int = 0
		self.save_skips_used: int = 0

		# Various Death Link booleans
		self.caused_deathlink: bool = False
		self.died_to_deathlink: bool = False
		self.pending_received_deathlink: bool = False
		self.deathlink_enabled: bool = False

		# Misc. game stats
		self.is_game_running: bool = False
		self.is_loading_data_setup: bool = True
		self.completed_loading_save_data: bool = False

		self.reset_context()

	def reset_context(self):
		self.previous_location_checked = []
		self.all_location_ids = []
		self.handler = None
		self.in_error = False
		self.is_connected = False
		self.all_received_items = []
		self.loaded_past_received_items = False
		self.last_received_item_index_server = -1

		self.save_data_a = 0x0
		self.save_data_b = 0x0
		self.save_playtime = 0
		self.save_deaths = 0
		self.save_skips_used = 0

		self.caused_deathlink = False
		self.died_to_deathlink = False
		self.pending_received_deathlink = False
		self.deathlink_enabled = False

		self.is_game_running = False
		self.retrieved_custom_data = False
		self.completed_loading_save_data = False

	def make_gui(self):
		ui = super().make_gui()
		ui.base_title = f"{DISPLAY_NAME} Client"
		return ui

	async def server_auth(self, password_requested: bool = False):
		if password_requested and not self.password:
			await super().server_auth(password_requested)
		await self.get_username()
		await self.send_connect()

	# TODO: Item handling
	def on_package(self, cmd: str, args: dict):
		"""
		Manage the package received from the server
		"""
		if cmd == "RoomInfo":
			self.seed_name = args["seed_name"]

		if cmd == "Connected":
			self.previous_location_checked = args["checked_locations"]
			self.all_location_ids = set(args["missing_locations"] + args["checked_locations"])
			self.options = args["slot_data"] # .yaml Options and Other Fields
			self.is_connected = True
			self.slot = args["slot"]

			if self.handler is not None:
				self.handler.reset()

			asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": [DISPLAY_NAME]}]))

		if cmd == "ReceivedItems":
			pass
			asyncio.create_task(
				self.handle_received_items(network_index=args["index"],
										   network_items_list=args["items"])
			)

		# Custom data goes here.
		elif cmd == "Retrieved":
			for data_index in range(len(self.custom_data_keys_list)):
				if self.custom_data_keys_list[data_index] in args["keys"]:
					if args["keys"][self.custom_data_keys_list[data_index]] is not None:
						new_data = self.custom_data_keys_list[data_index]
						match data_index:
							# Save Data A (512 bits only)
							case 0:
								self.save_data_a = new_data
							# Save Data B (512 bits only)
							case 1:
								self.save_data_b = new_data
							# Playtime Accumulated (Maxes out at 3 600 000)
							case 2:
								self.save_playtime = clamp(new_data, 0, CONST_MAX_PLAYTIME_CLIENT)
							# Death Count (Maxes out at 300)
							case 3:
								self.save_deaths = clamp(new_data, 0, CONST_MAX_DEATHS_CLIENT)
							# Scene Skips Used Count (Maxes out at 75)
							case 4:
								self.save_skips_used = clamp(new_data, 0, CONST_MAX_SCENE_SKIPS)
							case _:
								logger.info(f"Unknown index in custom data keys list. Skipping load for this one...")

		elif cmd == "DataPackage":
			if not self.all_location_ids: return
			self.location_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["location_name_to_id"]
			self.location_name_to_ap_id = {
				name: loc_id for name, loc_id in
				self.location_name_to_ap_id.items() if loc_id in self.all_location_ids
			}
			self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
			self.item_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["item_name_to_id"]
			self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}

		elif cmd == "Bounced":
			tags = args.get("tags", [])
			# Skip checking if DeathLink is in ctx.tags. Wouldn't have been sent this otherwise.
			if "DeathLink" in tags and self.last_death_link != args["data"]["time"]:
				self.last_death_link = args["data"]["time"]
				self.on_deathlink(args["data"])

	def client_received_initial_server_data(self):
		"""
		This method waits until the client finishes the initial conversation with the server.
		This means:
			- All LocationInfo packages received - requested only if patch files don't exist.
			- DataPackage package received (id_to_name maps and name_to_id maps are populated)
			- Connection package received (slot number populated)
			- RoomInfo package received (seed name populated)
		"""
		return self.is_connected

	#
	# Connection functions
	#
	async def wait_for_initial_connection_info(self):
		"""
		This method waits until the client finishes the initial conversation with the server.
		See client_recieved_initial_server_data for wait requirements.
		"""
		if self.client_received_initial_server_data():
			return

		logger.info("Waiting for connection from the server...")
		while not self.client_received_initial_server_data() and not self.exit_event.is_set():
			await asyncio.sleep(1)

	async def connect_to_game(self):
		"""
		Connect the client to the game process.
		"""
		self.handler = None

		while self.handler is None:
			try:
				self.handler: GameHandler = GameHandler()
			except Exception as e:
				await asyncio.sleep(2)

	async def reconnect_to_game(self):
		"""
		Reconnect to the game without resetting everything
		"""

		while self.handler.gameController is None:
			try:
				self.handler.reconnect()
			except Exception as e:
				await asyncio.sleep(2)

	def logger_debug(self, debug_msg: str):
		logger.info(debug_msg)

	#
	# Function that checks if the main bulk of the client should be running or not.
	#
	def should_not_be_running_context(self) -> bool:
		return self.handler is None or self.handler.gameController is None or not self.handler.is_game_running()

	# TODO
	# Custom Data from Server
	#
	async def get_custom_data_from_server(self):
		self.retrieved_custom_data = True
		await self.send_msgs([{"cmd": "Get", "keys": self.custom_data_keys_list}])
		await self.send_msgs([{"cmd": "SetNotify", "keys": self.custom_data_keys_list}])

	# TODO
	# Handle incoming items
	#
	async def handle_received_items(self, network_index, network_items_list):
		"""
		        Handle items received from the server. Since some save data is also
		        embedded into the items list, the index will be ignored for them specifically.
		        The rest of the items are separated into queues and processed simultaneously.
		        """
		# Wait until the game is online and the client is not having issues before processing the items.
		while self.should_not_be_running_context() or self.in_error:
			await asyncio.sleep(0.5)

		network_item_in_id: list[int] = []
		for network_item in network_items_list:
			network_item_in_id.append(network_item.item)

		# Python slicing will exclude the index of the start point if it's a positive integer.
		# Before actually processing it, wait until the client has loaded the local list of received items.
		while not self.loaded_past_received_items or self.last_received_item_index_server <= -1:
			await asyncio.sleep(0.5)

		local_list_length = len(self.all_received_items)

		newly_received_items: list[NetworkItem] = []

		# Upon receiving this package, check if the index is 0.
		# If it is, bring up the loaded local item list. Grab the length of that local list.
		# Slice the server's list from that number onwards. Only process that.
		if network_index <= 0:
			# If the server's list is somehow shorter than the local one,
			# this is probably divergent history.
			if len(network_items_list) < local_list_length:
				self.logger_debug("Received item list is somehow smaller than the local list. Divergent history?")
				self.all_received_items = []
				for network_item in network_items_list:
					self.all_received_items.append(network_item.item)
				await self.write_last_item_list()
				return
			# Otherwise, business as usual.
			newly_received_items = network_items_list[local_list_length:]
		# If the index is not 0, check for the most common case first.
		else:
			# If the index is the same as the local list's length, process that as per usual.
			if network_index == local_list_length: newly_received_items = network_items_list
			# If the index is different, request a Sync.
			else:
				self.logger_debug(f"Received index {str(network_index)} does not match what the client expected {str(local_list_length)}.")
				sync_msg = [{'cmd': 'Sync'}]
				if self.locations_checked:
					sync_msg.append({"cmd": "LocationChecks",
									 "locations": list(self.locations_checked)})
				await self.send_msgs(sync_msg)

		# Save data items do not care about index.
		self.handle_save_data_items(network_items_list)
		# Safeguard if there are no newly received items.
		if len(newly_received_items) <= 0: return
		self.handle_filler_items(newly_received_items)
		await self.add_to_item_list(newly_received_items)

	# Save data items
	def handle_save_data_items(self, network_item_list: list[NetworkItem]):
		day_unlock_count: int = 0
		scene_unlock_list = []
		item_level_list = []
		item_count_list = []
		item_stat_list = []
		subitem_unlock_list = []

		for network_item in network_item_list:
			# Individually check each received item's code.
			if network_item.item == item_table[CONST_PROGRESSIVE_DAY]:
				day_unlock_count += 1
			elif network_item.item == item_table[CONST_SUBITEM_SLOT_NAME]:
				pass
			elif network_item.item <= 10:
				scene_unlock_list.append(network_item.item)
			elif 12 <= network_item.item <= 20: pass
			elif 21 <= network_item.item <= 29: pass
			elif 32 <= network_item.item <= 40: pass
			elif 51 <= network_item.item <= 59: pass
			elif 41 <= network_item.item <= 48: pass

	# TODO: Call update_days in the Handler after this. Write that too.
	def handle_days_unlocked(self, day_unlock_list):
		pass

	# TODO: Call update_scenes in the Handler after this. Write that too.
	def handle_scenes_unlocked(self, scene_unlock_list):
		pass

	# TODO: Call update_cheat_items in the Handler after this. Write that too.
	def handle_cheat_items(self, filtered_list):
		pass

	async def handle_treasure_hunt(self, treasure_count):
		pass

	# Filler
	def handle_filler_items(self, filtered_list):
		pass

	async def handle_game_only_items(self):
		pass

	async def handle_menu_only_items(self):
		pass

	#
	# Victory Condition
	#
	def check_victory_conditions(self) -> bool:
		completion_type = self.options["completion_type"]

		match completion_type:
			case 0:
				return self.handler.get_day_clear_count(10) > 3
			case 1:
				return self.handler.get_day_clear_count(10) >= 10
			case 2:
				return self.handler.get_all_days_clear_minimum(4)
			case 3:
				return self.handler.get_all_days_all_clear()
			case 4:
				return self.handler.get_all_nicknames_check(False)
			case 5:
				return self.handler.get_all_nicknames_check(self.options["include_hidden_nicknames"])
			case 6:
				return self.handler.get_treasure_condition()

		return False

	#
	# Update locations checked
	#
	def location_table_check(self, given_location) -> bool:
		"""
		Checks if:
		- This location exists in the location table or not.
		- This location has already been checked or not.
		- Is in All Locations IDs or not.
		If any of that fails, immediately return False.
		"""
		if given_location not in location_table: return False
		if given_location not in self.all_location_ids: return False
		if given_location not in self.locations_checked: return False
		return True

	async def update_locations_checked(self):
		"""
		Check if any locations has been checked since this was last called.
		If there is, send a message and update the checked location list.
		"""
		if self.is_loading_data_setup or not self.completed_loading_save_data: return

		new_locations = []

		# Scene Clears
		if self.handler.is_game_paused():
			for day_id in range(10):
				for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
					used_day_id: int = day_id + 1
					used_scene_id: int = scene_id + 1

					if self.handler.get_scene_generic_clear((used_day_id, used_scene_id)):
						generic_location_name = get_location_name_scene(used_day_id, used_scene_id)
						if self.location_table_check(generic_location_name):
							new_locations.append(location_table[generic_location_name])
					if not self.options["include_item_clears"]: continue
					for item_id in range(10):
						if self.handler.get_scene_item_clear((used_day_id, used_scene_id), item_id):
							item_location_name = get_location_name_scene_with_item(used_day_id, used_scene_id,
																					   item_id)
							if not self.location_table_check(item_location_name): continue
							new_locations.append(location_table[item_location_name])

		# Nicknames
		for i in range(CONST_TOTAL_NICKNAME_COUNT):
			if not self.options["include_hidden_nicknames"] and i >= (CONST_TOTAL_NICKNAME_COUNT - 10):
				continue
			if not self.handler.get_nickname_check(i): continue
			nickname_location_name = get_location_name_nickname(i + 1)
			if not self.location_table_check(nickname_location_name): continue
			new_locations.append(location_table[nickname_location_name])

		# Music Room
		if self.options["include_music_checks"]:
			for i in range(9):
				if not self.handler.get_music_check(i): continue
				music_location_name = get_location_name_music_room(i + 1)
				if not self.location_table_check(music_location_name): continue
				new_locations.append(location_table[music_location_name])

		# If there are new locations, send a message to the server
		# and add to the list of previously checked locations.
		if new_locations:
			self.previous_location_checked = self.previous_location_checked + new_locations
			await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

		if self.check_victory_conditions() and not self.finished_game:
			self.finished_game = True
			await self.send_msgs([{"cmd": 'StatusUpdate', "status": 30}])

	async def update_event_save_data(self):
		"""
		Intended to be called exclusively while the game is paused and in a stage.
		May be called if a Scene Skip was used.
		"""
		def is_scene_not_internally_checked(day_scene_tuple: tuple[int, int], item_id: int) -> bool:
			if self.retrieve_save_data_ab(day_scene_tuple, item_id): return False
			if not self.handler.get_scene_item_clear(day_scene_tuple, item_id): return False
			return True

		has_updated_event_save: bool = False

		for day_id in range(10):
			for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
				used_day_tuple: tuple[int, int] = (day_id + 1, scene_id + 1)

				for item_id in range(10):
					if not is_scene_not_internally_checked(used_day_tuple, item_id): continue
					self.update_check_save_data_ab(
						day_scene_tuple=used_day_tuple,
						item_id=item_id
					)
					has_updated_event_save = True

		if not has_updated_event_save: return
		await self.write_event_save_data_ab()

	def update_check_save_data_ab(self, day_scene_tuple: tuple[int, int] = (1, 1), item_id: int = 0):
		old_data_tuple: tuple[int, int] = (self.save_data_a, self.save_data_b)
		self.save_data_a, self.save_data_b = set_scene_clear_neutral(
			save_data_ab=old_data_tuple,
			day_scene_id=day_scene_tuple,
			item_id=item_id,
			value=True
		)
		if self.save_data_a < 0: self.save_data_a = 0
		if self.save_data_b < 0: self.save_data_b = 0

	def retrieve_save_data_ab(self, day_scene_tuple: tuple[int, int] = (1, 1), item_id: int = 0) -> bool:
		return get_scene_clear_neutral(
			save_data_ab=(self.save_data_a, self.save_data_b),
			day_scene_id=day_scene_tuple,
			item_id=item_id
		)

	#
	# Server Interaction Functions
	#
	async def write_event_save_data_ab(self):
		list_msg_to_send: list[dict] = [{
			"cmd": 'Set',
			"key": self.custom_data_keys_list[0],
			"default": 0,
			"operations": [{"operation": 'or', "value": self.save_data_a}]
		}, {
			"cmd": 'Set',
			"key": self.custom_data_keys_list[1],
			"default": 0,
			"operations": [{"operation": 'or', "value": self.save_data_b}]
		}]

		await self.send_msgs(list_msg_to_send)

	async def write_playtime_to_server(self):
		await self.send_msgs([{
			"cmd": 'Set',
			"key": self.custom_data_keys_list[2],
			"default": 0,
			"operations": [{"operation": 'replace', "value": clamp(self.save_playtime, 0, CONST_MAX_PLAYTIME_CLIENT)}]
		}])

	async def write_death_stat_to_server(self):
		await self.send_msgs([{
			"cmd": 'Set',
			"key": self.custom_data_keys_list[3],
			"default": 0,
			"operations": [{"operation": 'replace', "value": clamp(self.save_deaths, 0, CONST_MAX_DEATHS_CLIENT)}]
		}])

	async def write_scene_skip_to_server(self):
		await self.send_msgs([{
			"cmd": 'Set',
			"key": self.custom_data_keys_list[4],
			"default": 0,
			"operations": [{"operation": 'max', "value": clamp(self.save_skips_used, 0, CONST_MAX_SCENE_SKIPS)}]
		}])

	#
	# Save data
	#
	def clear_save_data(self):
		"""
		Should only be called when first connecting to the game.
		"""
		self.handler.set_default_item_data()
		self.clear_save_data_scene()
		self.clear_save_data_other()
		return

	def clear_save_data_scene(self):
		for day_id in range(10):
			for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
				day_scene_tuple: tuple[int, int] = (day_id + 1, scene_id + 1)

				self.handler.set_scene_generic_clear(day_scene_tuple, False)
				for item_id in range(10):
					self.handler.set_scene_item_clear(
						day_scene_tuple,
						item_id,
						False
					)

		return

	def clear_save_data_other(self):
		for nickname_id in range(CONST_TOTAL_NICKNAME_COUNT):
			self.handler.set_nickname_check(nickname_id, False)
		for music_id in range(9):
			self.handler.set_music_check(music_id, False)
		return

	async def load_save_data(self):
		while self.should_not_be_running_context():
			await asyncio.sleep(0.5)

		while self.handler.get_music_check(0):
			self.clear_save_data()
			await asyncio.sleep(1.0)

		# Item Equip data is loaded when items from the AP server is received.
		# Not here.

		self.load_save_data_scene_generic()
		self.load_save_data_scene_items()
		self.load_save_data_other()
		self.handler.options = self.options

		return

	def load_save_data_scene_generic(self):
		# Go through Locations list.
		for day_id in range(10):
			for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
				generic_clear_location_name: str = get_location_name_scene(
					day_number=day_id + 1,
					scene_number=scene_id + 1
				)
				if not location_table[generic_clear_location_name] in self.locations_checked: continue
				self.handler.set_scene_generic_clear(
					day_and_scene_id=(day_id + 1, scene_id + 1),
					value=True
				)

		return

	def load_save_data_scene_items(self):
		# Rely on internal data.
		for day_id in range(10):
			for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
				for item_id in range(10):
					if get_scene_clear_neutral(
						save_data_ab=(self.save_data_a, self.save_data_b),
						day_scene_id=(day_id + 1, scene_id + 1),
						item_id=item_id
					):
						self.handler.set_scene_item_clear(
							day_and_scene_id=(day_id + 1, scene_id + 1),
							item_id=item_id,
							value=True
						)

		return

	def load_save_data_other(self):
		# Nicknames and Music Room should rely on Locations list.
		for nickname_id in range(CONST_TOTAL_NICKNAME_COUNT):
			if not self.options["include_hidden_nicknames"] and nickname_id >= (CONST_TOTAL_NICKNAME_COUNT - 10):
				continue
			nickname_location_name: str = get_location_name_nickname(nickname_id + 1)
			if not location_table[nickname_location_name] in self.locations_checked: continue
			self.handler.set_nickname_check(nickname_id, True)

		for music_id in range(9):
			music_location_name: str = get_location_name_music_room(music_id + 1)
			if not location_table[music_location_name] in self.locations_checked: continue
			self.handler.set_music_check(music_id, True)

		return

	# TODO
	# Game Transfer between Menu and Stage
	#
	async def transfer_from_menu_to_stage(self):
		"""
		Handles transferring from the game menu to stage.
		"""
		pass

	async def transfer_from_stage_to_menu(self):
		"""
		Handles transferring from stage to the game menu.
		"""
		pass

	# TODO
	# Stage Reset
	#
	async def stage_reset_async(self):
		pass

	# TODO
	# Last Received Item Index handling.
	#
	# The data is saved in a .json named "th143ap_????.json", where ???? is the seed name.
	# The data consists of a Dictionary, wherein there is the slot name and received item list.
	# Only do this after connection has been established since this calls for the seed name and slot name.
	#
	# Use orjson functions for dealing with said .json.
	async def initial_load_last_item_list(self):
		# Responsible for loading the index of the last item received when client connects to the server.
		# The usual workflow of this function is as follows:
		# 1. Check if the file exists in the path.
		# 2. If the file exists, read the entire file as one Dictionary.
		# 3. Check if the slot name matches and if the item list exists.
		# 5. Read the item list as a list.
		#
		# If at any point that any of the steps above fail, skip the entire thing.

		# Check if this operation has already been carried out before.
		if self.loaded_past_received_items: return

		json_file_name = get_item_index_save_name(self.seed_name, self.team, self.slot)
		full_file_path = os.path.join(user_path(CLIENT_DATA_PATH), os.path.basename(json_file_name))

		# Check if the file exists.
		if os.path.exists(full_file_path):
			with open(full_file_path) as json_file:
				saved_data_dict: dict = orjson.loads(json_file.read())
				# Check if the slot name matches and item list exists.
				if JSON_SLOT_ITEMS in saved_data_dict:
					self.all_received_items = saved_data_dict[JSON_SLOT_ITEMS]
				if JSON_SLOT_CLEARS_A in saved_data_dict:
					self.save_data_a = saved_data_dict[JSON_SLOT_CLEARS_A]
				if JSON_SLOT_CLEARS_B in saved_data_dict:
					self.save_data_b = saved_data_dict[JSON_SLOT_CLEARS_B]
				if JSON_SLOT_PLAYTIME in saved_data_dict:
					self.save_playtime = saved_data_dict[JSON_SLOT_PLAYTIME]
				if JSON_SLOT_DEATHS in saved_data_dict:
					self.save_deaths = saved_data_dict[JSON_SLOT_DEATHS]
				if JSON_SLOT_SCENE_SKIP in saved_data_dict:
					self.save_skips_used = saved_data_dict[JSON_SLOT_SCENE_SKIP]

		self.loaded_past_received_items = True
		return

	async def add_to_item_list(self, item_list: list[NetworkItem]):
		# Adds item to the list of received items.
		# Call the function to write the item list to a local file afterwards.
		if item_list is None or item_list == []:
			return

		item_id_list: list[int] = []
		for network_item in item_list:
			item_id_list.append(network_item.item)

		self.all_received_items += item_id_list

		await self.write_last_item_list()

	async def write_last_item_list(self):
		# Writes the last received item index to a .json file named "th185ap".
		# Initial check to make sure the client has not reset itself.
		if not self.is_connected and not self.inError: return
		if len(self.all_received_items) <= 0: return

		json_file_name = get_item_index_save_name(self.seed_name, self.team, self.slot)
		full_file_path = os.path.join(user_path(CLIENT_DATA_PATH), os.path.basename(json_file_name))

		full_dict = {
			JSON_SLOT_NAME: self.player_names[self.slot],
			JSON_SLOT_ITEMS: self.all_received_items,
			JSON_SLOT_CLEARS_A: self.save_data_a,
			JSON_SLOT_CLEARS_B: self.save_data_b,
			JSON_SLOT_PLAYTIME: self.save_playtime,
			JSON_SLOT_DEATHS: self.save_deaths,
			JSON_SLOT_SCENE_SKIP: self.save_skips_used
		}

		client_directory_get_or_default()

		# Remove the old file before writing.
		if os.path.exists(full_file_path):
			os.remove(full_file_path)
		# Overwrite the entire thing.
		with open(full_file_path, "wb") as json_file:
			json_file.write(orjson.dumps(full_dict))

		# Write this to the server. No need to wait for it, though.
		# It's just a backup measure if local data is somehow gone.
		#asyncio.create_task(self.save_last_index_to_server())
		return

	# TODO
	# Several Death Link functionalities
	#
	def on_deathlink(self, data: dict[str, Any]) -> None:
		"""
		Called when receiving a Death Link from the server.
		"""
		self.pending_received_deathlink = True
		if not self.handler.is_game_in_stage():
			self.pending_received_deathlink = False
		return super().on_deathlink(data)

	async def send_deathlink(self):
		"""
		Sends a Deathlink to the server, if the server is active.
		"""
		# If Death Link is not enabled, don't send anything.
		if not self.deathlink_enabled: return
		#await self.send_death(self.player_names[self.slot] + get_random_death_message(self.handler.getCurrentStage(),
		#																			  self.handler.getLastBossMet(),
		#																			  self.lost_final_life))
		await self.send_death(self.player_names[self.slot])

	def reset_deathlink_stats(self):
		self.pending_received_deathlink = False
		self.died_to_deathlink = False
		self.caused_deathlink = False

	# TODO
	# Game loops
	#
	def should_run_loop(self) -> bool:
		if self.exit_event.is_set() or not self.handler or self.in_error: return False
		return True

	async def main_loop(self):
		pass

	async def menu_loop(self):
		pass

	async def stage_loop(self):
		pass

	async def trap_loop(self):
		pass

	async def deathlink_loop(self):
		pass


# Game Watcher
async def game_watcher_async(ctx: ContextISC):
	"""
	Client loop that watches the gameplay progress.
	Start the different loops once connected that will handle the game.
	It will also attempt to reconnect if the connection to the game is lost.
	"""
	await ctx.wait_for_initial_connection_info()
	await ctx.initial_load_last_item_list()

	while not ctx.exit_event.is_set():
		# Client was disconnected from the server
		if not ctx.server:
			# Reset the context in that case
			if ctx.is_connected:
				logger.info("Client was disconnected from the server.")
			ctx.reset_context()
			await ctx.wait_for_initial_connection_info()
			await ctx.initial_load_last_item_list()
		else:
			if not ctx.retrieved_custom_data:
				try:
					await ctx.get_custom_data_from_server()
				except Exception as e:
					ctx.in_error = True
					logger.error("Failed to retrieve save data.")
					logger.error(traceback.format_exc())

		# Trying to make first connection to the game
		if ctx.handler is None and not ctx.in_error:
			logger.info(f"Trying to find {SHORT_NAME} game process...")
			asyncio.create_task(ctx.connect_to_game())
			while ctx.handler is None and not ctx.exit_event.is_set():
				await asyncio.sleep(1)

		# Trying to reconnect to the game after an error
		if ctx.in_error or (ctx.handler.gameController is None and not ctx.exit_event.is_set()) and ctx.retrieved_custom_data:
			if ctx.in_error:
				logger.info(f"Connection was lost. Attempting reconnection...")
			ctx.handler.gameController = None
			ctx.loadingDataSetup = True

			asyncio.create_task(ctx.reconnect_to_game())
			await asyncio.sleep(1)

			while ctx.handler.gameController is None and not ctx.exit_event.is_set():
				await asyncio.sleep(1)

		# No connection issues. Start loops.
		if ctx.handler and ctx.handler.gameController:
			ctx.in_error = False

			if not ctx.is_game_running:
				ctx.is_game_running = ctx.handler.gameController.check_if_in_game()
				await asyncio.sleep(1)
				continue

			if ctx.is_loading_data_setup:
				logger.info(f"Found {SHORT_NAME} process!")

				# Set default Trap times
				# Check if Death Link is enabled
				if ctx.options["death_link"]:
					await ctx.update_death_link(True)
					ctx.deathlink_enabled = True

				asyncio.create_task(ctx.load_save_data())
				ctx.is_loading_data_setup = False
				continue

			# Start the different loops.
			loops = [
				asyncio.create_task(ctx.main_loop()),
				asyncio.create_task(ctx.menu_loop()),
				asyncio.create_task(ctx.stage_loop()),
				asyncio.create_task(ctx.trap_loop())
			]
			if ctx.deathlink_enabled:
				loops.append(asyncio.create_task(ctx.deathlink_loop()))

			# Infinitely loop if there is no error.
			while not ctx.exit_event.is_set() and not ctx.inError and ctx.server:
				await asyncio.sleep(1)
			# If there is, exit to restart the connection.
			# Stop all loops if possible at this phase.
			if ctx.exit_event.is_set():
				# Save index here.
				pass

			logger.info("Cancelling game loops...")
			for loop in loops:
				try: loop.cancel()
				except: pass

# Client Window
def client_launch():
	"""
	Launch a client instance (wrapper / args parser)
	"""

	async def main(args):
		"""
		Launch a client instance (threaded)
		"""
		ctx = ContextISC(args.connect, args.password)
		ctx.server_task = asyncio.create_task(server_loop(ctx))
		if gui_enabled: ctx.run_gui()
		ctx.run_cli()
		watcher = asyncio.create_task(
			game_watcher_async(ctx),
			name="GameProgressionWatcher"
		)
		await ctx.exit_event.wait()
		await watcher
		await ctx.shutdown()

	parser = get_base_parser(description=SHORT_NAME + " Client")
	args, _ = parser.parse_known_args()

	Utils.init_logging("HBMClient")

	colorama.init()
	asyncio.run(main(args))
	colorama.deinit()