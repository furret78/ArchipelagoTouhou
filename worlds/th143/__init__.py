from typing import Mapping, Any

from worlds.AutoWorld import World
from .client.webworld import ISCWebWorld
from .worldgen.world_options import options
from .worldgen.world_options.options_classes import StartingDay, CompletionType
from .utils.utils_get_name import get_scene_unlock_name, get_item_name_usage, get_item_name_stat, get_item_name_level
from .utils.utils_math import clamp
from .variables.game_info import DISPLAY_NAME, SHORT_NAME, CLIENT_DESCRIPTION
from .variables.location_item_name import CONST_DAY_TO_ID, CONST_PROGRESSIVE_DAY, CONST_TREASURE_ITEM_NAMES
from .worldgen import regions, items
from .worldgen.world_locations import location_table
from .worldgen.world_locations import locations
from .worldgen.world_rules import rules
from ..LauncherComponents import launch_subprocess, components, Component, Type, icon_paths


def launch_client():
	"""
	Launch an instance of the game client.
	"""
	from .client.client_main import client_launch
	launch_subprocess(client_launch, name="GameClient")

components.append(Component(
	display_name=f"{SHORT_NAME} Client",
	description=CLIENT_DESCRIPTION,
	func=launch_client,
	component_type=Type.CLIENT,
	game_name=DISPLAY_NAME,
	icon="th143_icon"
))

icon_paths["th143_icon"] = f"ap:{__name__}/icons/th185_card.png"

class ISCWorld(World):
	"""
	The amanojaku, Seija Kijin.
	She used the treasure of the inchlings, the "Miracle Mallet", in an attempt to conquer Gensokyo.
	Though her plot ended in failure, she would not give up yet.
	Knowing that the Mallet's magic had caused items to move on their own,
	she secretly gathered those items unbeknownst to their owners.
	"If I collect the remaining magic in these, then maybe..."
	But some way or another, that plot was found out as well.
	One by one, youkai began to appear before her, deeming her a rebel plotting an upheaval of Gensokyo's society.
	The youkai would show no regard for rules in their danmaku.
	You don't need to hesitate; Drive them away with the cursed tools!
	(from en.touhouwiki.net)
	"""
	game = DISPLAY_NAME
	web = ISCWebWorld()

	location_name_to_id = location_table.location_table
	location_id_to_name = location_table.location_table_reverse
	item_name_to_id = items.get_item_to_id_dict()

	options_dataclass = options.ISCDataclass
	options: options.ISCDataclass

	origin_region_name = "Menu"

	item_name_groups = items.get_item_groups()
	location_name_groups = location_table.location_groups

	selected_random_starting_days: list[str]
	treasure_count_needed: int

	def generate_early(self) -> None:
		# TODO: Remove these things and work on their parts.
		if self.options.skill_difficulty.value != 1:
			self.options.skill_difficulty.value = 1
		if self.options.include_itemless_logic:
			self.options.include_itemless_logic.value = False
		if self.options.item_upgrade_progress.value != 0:
			self.options.item_upgrade_progress.value = 0
		# TODO: Remove these things and work on their parts.

		self.treasure_count_needed = 0
		self.selected_random_starting_days = []

		# If Randomized Start is enabled, randomize it here.
		if self.options.starting_day == StartingDay.option_random_day:
			valid_random_pool = []
			if len(self.options.valid_starting_days.value) <= 0:
				self.options.valid_starting_days.value = CONST_DAY_TO_ID.keys()
			for i in self.options.valid_starting_days.value:
				valid_random_pool.append(i)

			self.options.starting_day_random_range.value = clamp(
				self.options.starting_day_random_range.value, 1, len(self.options.valid_starting_days.value) - 1
			)

			if self.options.progressive_day:
				self.options.starting_day_random_range.value = 1

			rand_count = 0
			while rand_count < self.options.starting_day_random_range.value:
				random_chosen_day = self.random.choice(valid_random_pool)
				if random_chosen_day not in self.selected_random_starting_days:
					self.selected_random_starting_days.append(random_chosen_day)
					rand_count += 1
				else: continue

		# If the length of this is greater than 0, it means Randomized Start is active.
		if len(self.selected_random_starting_days) > 0:
			# If Progressive Day is enabled, only 1 Day was chosen.
			# Push as many Progressive Day items as possible to reach that Day.
			if self.options.progressive_day:
				item_count_needed: int = CONST_DAY_TO_ID[self.selected_random_starting_days[0]]
				if item_count_needed > 0:
					for k in range(item_count_needed):
						self.push_precollected(self.create_item(CONST_PROGRESSIVE_DAY))
			# Otherwise, push Progressive Scene for the Days that have been unlocked.
			else:
				for day_str in self.selected_random_starting_days:
					day_id_from_str: int = CONST_DAY_TO_ID[day_str] + 1
					self.push_precollected(self.create_item(get_scene_unlock_name(day_id_from_str)))
		# Otherwise, continue as though it was not active.
		else:
			if self.options.progressive_day:
				item_count_needed: int = self.options.starting_day.value
				if item_count_needed > 0:
					for k in range(item_count_needed):
						self.push_precollected(self.create_item(CONST_PROGRESSIVE_DAY))
			else:
				day_id_from_str: int = self.options.starting_day.value + 1
				self.push_precollected(self.create_item(get_scene_unlock_name(day_id_from_str)))

		# For fun, if the goal is Gold Rush, add the Miracle Mallet (Real) to the player's inventory.
		# It does absolute fuck-all, but it's a funny easter egg.
		if self.options.completion_type == CompletionType.option_gold_rush:
			self.push_precollected(self.create_item(CONST_TREASURE_ITEM_NAMES[1]))

		# If a Starting Cheat Item was chosen, push precollected that here.
		# Remember to avoid generating more of it later.
		if 0 <= self.options.starting_cheat_item < 9:
			internal_item_id: int = self.options.starting_cheat_item.value
			if self.options.item_upgrade_separate:
				self.push_precollected(self.create_item(get_item_name_usage(internal_item_id)))
				self.push_precollected(self.create_item(get_item_name_stat(internal_item_id)))
			else:
				self.push_precollected(self.create_item(get_item_name_level(internal_item_id)))

		return

	def create_regions(self):
		regions.create_and_connect_regions(self)
		locations.create_all_locations(self)

	def set_rules(self) -> None:
		rules.set_all_rules(self)

	def create_items(self) -> None:
		items.create_all_items(self)

	def create_item(self, name: str) -> items.ISCItem:
		return items.create_item_with_correct_classification(self, name)

	def get_filler_item_name(self) -> str:
		return items.get_random_filler_item_name(self)

	# The place where player data goes.
	def fill_slot_data(self) -> Mapping[str, Any]:
		data = {
			"skill_difficulty": self.options.skill_difficulty.value,
			"trap_chance": self.options.trap_chance.value,
			"trap_blacklist": self.options.trap_blacklist.value,
			"death_link": self.options.death_link.value,
			"death_link_amnesty": self.options.death_link_amnesty.value,
			"death_link_anti": self.options.death_link_anti.value,
			"completion_type": self.options.completion_type.value,
			"treasure_required": self.options.treasure_required.value,
			"treasure_percent": self.options.treasure_percent.value,
			"progressive_day": self.options.progressive_day.value,
			"progressive_scene": self.options.progressive_scene.value,
			"starting_day": self.options.starting_day.value,
			"starting_day_random_range": self.options.starting_day_random_range.value,
			"valid_starting_days": self.options.valid_starting_days.value,
			"starting_cheat_item": self.options.starting_cheat_item.value,
			"item_upgrade_progress": self.options.item_upgrade_progress.value,
			"item_upgrade_separate": self.options.item_upgrade_separate.value,
			"item_upgrade_remove_cap": self.options.item_upgrade_remove_cap.value,
			"subitem_slot_unlock": self.options.subitem_slot_unlock.value,
			"subitem_individual": self.options.subitem_individual.value,
			"scene_skip_count": self.options.scene_skip_count.value,
			"useless_filler": self.options.useless_filler.value,
			"playtime_mult": self.options.playtime_mult.value,
			"include_music_checks": self.options.include_music_checks.value,
			"include_itemless_logic": self.options.include_itemless_logic.value,
			"include_item_clears": self.options.include_item_clears.value,
			"include_hidden_nicknames": self.options.include_hidden_nicknames.value,
			"treasure_count_needed": self.treasure_count_needed
		}
		return data