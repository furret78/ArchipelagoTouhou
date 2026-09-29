import asyncio
import logging

from CommonClient import ClientCommandProcessor
from ..utils.utils_math import clamp
from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ..variables.location_item_name import CONST_ITEM_NAMES

logger = logging.getLogger("Client")

class CommandProccessorISC(ClientCommandProcessor):
	def __init__(self, ctx):
		super().__init__(ctx)

	def check_cmd_should_run(self) -> bool:
		if not self.ctx.is_connected:
			logger.info(f"The client isn't connected to any servers!")
			return False
		if self.ctx.handler is None:
			logger.info(f"The game isn't running!")
			return False
		if not self.ctx.is_game_running:
			logger.info(f"The game isn't running!")
			return False

		return True

	async def scene_skip_cmd(self, daynum: int, scenenum: int):
		self.ctx.handler.do_scene_skip(daynum, scenenum)
		await self.ctx.update_locations_checked(True)
		logger.info(f"Used a Scene Skip to fully clear Scene {str(daynum)}-{str(scenenum)}.")
		return

	def _cmd_relink_game(self):
		"""
		Internally forces the client to enter Error state in order to restart link to the game.
		"""
		self.ctx.in_error = True

	def _cmd_check_item_clear(self, day_number: int, scene_number: int, item_id: int):
		"""
		Checks if a specific Scene from a specific Day was cleared with a specific Item.
		"""
		if not self.check_cmd_should_run(): return

		clean_day_id = clamp(int(day_number), 1, 10)
		clean_scene_id = clamp(int(scene_number), 1, CONST_DAY_SCENE_COUNT[clean_day_id - 1])
		clean_item_id = clamp(int(item_id), 0, 9)

		is_cleared = self.ctx.retrieve_save_data_ab(
			day_scene_tuple=(clean_day_id, clean_scene_id),
			item_id=clean_item_id
		)

		if clean_item_id < 9:
			item_name_str = f"with {CONST_ITEM_NAMES[clean_item_id]}"
		else: item_name_str = "without any items"

		logger.info(f"Is {clean_day_id}-{clean_scene_id} cleared {item_name_str}? {is_cleared}.")

	def _cmd_skip_scene(self, day_number: int, scene_number: int, force_override: str):
		"""
		Spends a Scene Skip item in order to skip the specified Scene.
		The 'force_override' parameter must be "yes" in order to proceed.
		Otherwise, this will check how many Scene Skip items have been used.
		"""
		if not self.check_cmd_should_run(): return

		scene_skip_count = self.ctx.get_total_scene_skip_count()
		scene_skip_used = self.ctx.save_skips_used

		if force_override != "yes":
			logger.info(f"Scene Skips used: {scene_skip_used}/{scene_skip_count}.")
			return
		if scene_skip_used >= scene_skip_count:
			logger.info(f"Not enough available Scene Skip items. Scene Skips already used: {scene_skip_used}/{scene_skip_count}.")
			return

		clean_day_id = clamp(int(day_number), 1, 10)
		clean_scene_id = clamp(int(scene_number), 1, CONST_DAY_SCENE_COUNT[clean_day_id - 1])
		scene_num_unlocked = self.ctx.handler.scenes_unlocked[clean_day_id - 1]

		if clean_scene_id > scene_num_unlocked:
			logger.info(f"Scene {str(clean_day_id)}-{str(clean_scene_id)} hasn't been unlocked yet. Cannot be skipped.")
			return
		if self.ctx.handler.get_scene_all_clear(clean_day_id, clean_scene_id):
			logger.info(f"Scene {str(clean_day_id)}-{str(clean_scene_id)} had already been fully cleared. Cannot be skipped.")
			return

		asyncio.create_task(self.scene_skip_cmd(clean_day_id, clean_scene_id))
		self.ctx.save_skips_used += 1
		asyncio.create_task(self.ctx.write_scene_skip_to_server())
		asyncio.create_task(self.ctx.save_new_local_data())
		return

	def _cmd_toggle_debug(self):
		"""
		Toggles whether debug messages should be shown or not.
		Will always default to False upon startup.
		Not recommended for normal gameplay.
		"""
		self.ctx.debug_messages_enabled = not self.ctx.debug_messages_enabled
		logger.info(f"Debug message showing has been updated to: {self.ctx.debug_messages_enabled}.")