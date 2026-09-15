from rule_builder.options import OptionFilter
from rule_builder.rules import Has, True_, False_, HasAnyCount, HasAllCounts, HasFromList
from ..world_locations.locations import get_fake_clear_item_name, get_fake_day_clear_item_name
from ..world_options.options_classes import SkillDifficulty, ProgressiveDay, ProgressiveScene, \
	ItemUpgradeSeparate, SubitemSlotUnlock, SubitemIndividual, IncludeItemlessLogic
from ...worldgen.items import get_vanilla_max_level_dict, get_vanilla_max_count_dict, get_vanilla_max_stat_dict, \
	get_vanilla_count_max, get_vanilla_level_max, get_vanilla_stat_max
from ...utils.utils_get_name import get_scene_unlock_name, get_item_name_level, get_item_name_usage, \
	get_item_name_stat, get_item_name_subitem
from ...utils.utils_math import clamp
from ...variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ...variables.location_item_name import CONST_PROGRESSIVE_DAY, CONST_ITEM_SHORT_TO_ID, CONST_SUBITEM_SLOT_NAME, \
	EVENT_ITEM_SCENE_UNLOCK_NAME, CONST_TREASURE_ITEM_NAMES
from ...variables.scene_clear_normal import *

#
# CONST
#
CONST_VANILLA_LOCKED_DAYS = (3, 5, 6, 8)

#
# VARIOUS OPTION FILTERS
#
# Difficulty
option_NormalMode = OptionFilter(SkillDifficulty, SkillDifficulty.option_normal)
option_HardMode = OptionFilter(SkillDifficulty, SkillDifficulty.option_hard)
option_LunaticMode = OptionFilter(SkillDifficulty, SkillDifficulty.option_lunatic)
# Progressive Day
option_ProgressiveDay_On = OptionFilter(ProgressiveDay, True)
option_ProgressiveDay_Off = OptionFilter(ProgressiveDay, False)
# Progressive Scene
option_ProgressiveScene_Vanilla = OptionFilter(ProgressiveScene, ProgressiveScene.option_original_vanilla)
option_ProgressiveScene_VanillaPlus = OptionFilter(ProgressiveScene, ProgressiveScene.option_vanilla_plus_one)
option_ProgressiveScene_FirstScene = OptionFilter(ProgressiveScene, ProgressiveScene.option_first_scene_only)
option_ProgressiveScene_Gradual = OptionFilter(ProgressiveScene, ProgressiveScene.option_gradual_unlock)
option_ProgressiveScene_Full = OptionFilter(ProgressiveScene, ProgressiveScene.option_full_unlock)
# Items and Sub-items
option_ItemUpgradeSeparate_On = OptionFilter(ItemUpgradeSeparate, True)
option_ItemUpgradeSeparate_Off = OptionFilter(ItemUpgradeSeparate, False)
option_SubitemSlot_On = OptionFilter(SubitemSlotUnlock, True)
option_SubitemSlot_Off = OptionFilter(SubitemSlotUnlock, False)
option_SubitemIndividual_On = OptionFilter(SubitemIndividual, True)
option_SubitemIndividual_Off = OptionFilter(SubitemIndividual, False)
# Logic
option_ItemlessLogic_On = OptionFilter(IncludeItemlessLogic, True)
option_ItemlessLogic_Off = OptionFilter(IncludeItemlessLogic, False)

# Item String ID to Clear Set Table
CONST_ITEM_SHORT_TO_CLEAR_SET = {
    "fabric": NORMAL_CLEAR_FABRIC_SET,
    "camera": NORMAL_CLEAR_CAMERA_SET,
    "umbrella": NORMAL_CLEAR_UMBRELLA_SET,
    "lantern": NORMAL_CLEAR_LANTERN_SET,
    "yinyang": NORMAL_CLEAR_YINYANG_SET,
    "bomb": NORMAL_CLEAR_BOMB_SET,
    "jizo": NORMAL_CLEAR_JIZO_SET,
    "doll": NORMAL_CLEAR_DOLL_SET,
    "mallet": NORMAL_CLEAR_MALLET_SET
}

#
# SCENE ACCESS RULES
#
def rule_require_day_access(day_id: int = 0):
	"""
	Days are indexed from 0 for this one.
	"""
	return Has(
		CONST_PROGRESSIVE_DAY,
		count=day_id,
		options=[option_ProgressiveDay_On],
		filtered_resolution=True
	)


def rule_require_scene_access(day_id: int = 1, scene_id: int = 1):
	"""
	Days and Scenes are indexed from 1 for this function.
	"""
	day_access = rule_require_day_access(day_id - 1)

	vanilla_unlock_requirement: int = 0
	if scene_id > 1: vanilla_unlock_requirement = 2

	vanilla_access = (option_ProgressiveScene_Vanilla & True_())
	if day_id in CONST_VANILLA_LOCKED_DAYS:
		vanilla_access = Has(
			get_scene_unlock_name(day_id),
			count=vanilla_unlock_requirement,
			options=[option_ProgressiveScene_Vanilla]
		)

	vanilla_plus_access = (option_ProgressiveScene_VanillaPlus & True_())
	if day_id in CONST_VANILLA_LOCKED_DAYS or day_id == 1:
		vanilla_plus_access = Has(
			get_scene_unlock_name(day_id),
			count=vanilla_unlock_requirement,
			options=[option_ProgressiveScene_VanillaPlus]
		)

	first_scene_access = Has(
		get_scene_unlock_name(day_id),
		count=clamp(scene_id, 1, 2),
		options=[option_ProgressiveScene_FirstScene]
	)

	gradual_access = Has(
		get_scene_unlock_name(day_id),
		count=scene_id,
		options=[option_ProgressiveScene_Gradual]
	)

	full_access = Has(
		get_scene_unlock_name(day_id),
		count=1,
		options=[option_ProgressiveScene_Full]
	)

	return day_access & (vanilla_access | vanilla_plus_access | first_scene_access | gradual_access | full_access)

def rule_multiple_scene_access(day_scene_tuples):
	"""
	Argument passed in should be in the form of ((1, 1), (2, 5)), etc.
	First number is the Day ID, second is Scene ID.
	"""
	multiple_scene_rule = False_()
	for day_scene_pair in day_scene_tuples:
		if day_scene_pair == (0, 0): break
		multiple_scene_rule = multiple_scene_rule | rule_require_scene_access(
			day_id=day_scene_pair[0],
			scene_id=day_scene_pair[1]
		)
	return multiple_scene_rule

#
# ITEM ACCESS RULES
#
def rule_require_specific_main_items(item_list: list[str]):
	"""
	item_list takes in the item string ID of the cheat items.
	The returned rule will be equivalent to HasAny().
	"""
	if len(item_list) <= 0: return True_()

	final_item_dict = {}
	for item_short, item_max in get_vanilla_max_level_dict().items():
		if item_short in item_list:
			item_id_from_string = CONST_ITEM_SHORT_TO_ID[item_short]
			final_item_dict[get_item_name_level(item_id_from_string)] = item_max

	final_count_dict = {}
	final_stat_dict = {}
	for count_short, count_max in get_vanilla_max_count_dict().items():
		if count_short in item_list:
			final_count_dict[count_short] = count_max
	for stat_short, stat_max in get_vanilla_max_stat_dict().items():
		if stat_short in item_list:
			final_stat_dict[stat_short] = stat_max

	final_rule = False_()

	for item_short_name in CONST_ITEM_SHORT_TO_ID.keys():
		if item_short_name not in item_list: continue
		item_id: int = CONST_ITEM_SHORT_TO_ID[item_short_name]

		final_rule = final_rule | HasAllCounts(
			{
				get_item_name_usage(item_id): final_count_dict[item_short_name],
				get_item_name_stat(item_id): final_stat_dict[item_short_name],
			}
		)

	return (HasAnyCount(final_item_dict, options=[option_ItemUpgradeSeparate_Off]) |
			(final_rule & option_ItemUpgradeSeparate_On))


def rule_require_specific_sub_items(sub_item_list: list[str]):
	"""
	item_list takes in the item string ID of the cheat items.
	The returned rule will be equivalent to HasAny() & Global Sub-item Unlock.
	"""
	subitem_unlock = Has(
		CONST_SUBITEM_SLOT_NAME,
		options=[option_SubitemSlot_On],
		filtered_resolution=True
	)

	subitem_id_list: list[int] = []
	for item_short in sub_item_list:
		subitem_id_list.append(CONST_ITEM_SHORT_TO_ID[item_short])

	subitem_individual = False_()
	for item_id in subitem_id_list:
		subitem_individual = subitem_individual | Has(
			get_item_name_subitem(item_id),
			options=[option_SubitemIndividual_On],
			filtered_resolution=True
		)

	return subitem_unlock & subitem_individual


def rule_require_one_main_item(item_string_id: str):
	if not item_string_id: return True_()
	item_id: int = CONST_ITEM_SHORT_TO_ID[item_string_id]

	level_rule = Has(get_item_name_level(item_id), count=get_vanilla_level_max(item_id),
				options=[option_ItemUpgradeSeparate_Off])
	separate_rule = HasAllCounts({
				get_item_name_usage(item_id): get_vanilla_count_max(item_id),
				get_item_name_stat(item_id): get_vanilla_stat_max(item_id)
			}, options=[option_ItemUpgradeSeparate_On])

	if item_string_id == "yinyang":
		separate_rule = HasAllCounts({
			get_item_name_usage(item_id): get_vanilla_count_max(item_id)
		}, options=[option_ItemUpgradeSeparate_On])

	return level_rule | separate_rule


def rule_require_one_sub_item(item_string_id: str):
	subitem_unlock = Has(
		CONST_SUBITEM_SLOT_NAME,
		options=[option_SubitemSlot_On],
		filtered_resolution=True
	)

	item_id: int = CONST_ITEM_SHORT_TO_ID[item_string_id]

	subitem_individual = Has(
		get_item_name_subitem(item_id),
		options=[option_SubitemIndividual_On],
		filtered_resolution=True
	)

	return subitem_unlock & subitem_individual


def rule_require_item_combo(item_tuple: tuple[str, str]):
	"""
	item_tuple is a tuple containing the Main Item string ID and Sub Item string ID.
	Intended only for specific item combinations.
	"""
	return rule_require_one_main_item(item_tuple[0]) & rule_require_one_sub_item(item_tuple[1])

#
# SCENE CLEAR CAPABILITY RULES
#
def rule_require_generic_clear(clear_count: int):
	return Has(get_fake_clear_item_name(10), count=clear_count)

def rule_require_day_clears(day_id: int = 1, clear_count: int = 0):
	"""
	Rule requiring a specific clear count from a Day.
	Day ID indexed from 1.
	"""
	return Has(get_fake_day_clear_item_name(day_id), count=clear_count)

def rule_require_item_clears(item_id: int = 0, clear_count: int = 0):
	"""
	Rule requiring a specific clear count using any certain item.
	Item ID indexed from 0. If 9, it's No-Item/Itemless.
	Any ID but 9 also includes Itemless clears.
	"""
	item_id_used: int = clamp(item_id, 0, 8)
	item_specific_clear_set = {
		get_fake_clear_item_name(item_id_used), get_fake_clear_item_name(9)
	}
	return HasFromList(*item_specific_clear_set, count=clear_count)

def get_very_specific_scene_rules(day_id: int, scene_id: int):
	"""
	Retrieves extra rules specific to a Scene.
	Should not be used outside of get_scene_rule()
	"""
	if scene_id in RULE_TABLE_SCENE_SPECIFIC[day_id - 1].keys():
		return RULE_TABLE_SCENE_SPECIFIC[day_id - 1][scene_id]
	return False_()

def get_scene_rule(day_id: int, scene_id: int):
	"""
	Retrieves the rule specific to a Scene.
	Day ID and Scene ID are indexed from 0.
	"""
	used_day_id: int = day_id + 1
	used_scene_id: int = scene_id + 1

	generic_scene_rule = rule_require_scene_access(
		day_id=day_id + 1,
		scene_id=scene_id + 1
	)

	specific_item_list = []
	# This retrieves a dict key-value pair.
	for item_name, item_clear_set in CONST_ITEM_SHORT_TO_CLEAR_SET.items():
		if check_if_scene_in_set(used_day_id, used_scene_id, item_clear_set):
			specific_item_list.append(item_name)
	# After the list has been filled,
	if len(specific_item_list) > 0:
		specific_scene_rule = rule_require_specific_main_items(specific_item_list)
	else:
		specific_scene_rule = False_()

	if check_if_scene_in_set(used_day_id, used_scene_id, NORMAL_CLEAR_DOLL_SUB_SET):
		specific_scene_rule = specific_scene_rule | rule_require_one_sub_item("doll")
	if check_if_scene_in_set(used_day_id, used_scene_id, NORMAL_CLEAR_JIZO_DOLL_SET):
		specific_scene_rule = specific_scene_rule | rule_require_item_combo(("jizo", "doll"))
	if check_if_scene_in_set(used_day_id, used_scene_id, NORMAL_CLEAR_LANTERN_DOLL_SET):
		specific_scene_rule = specific_scene_rule | rule_require_item_combo(("lantern", "doll"))
	if check_if_scene_in_set(used_day_id, used_scene_id, NORMAL_CLEAR_MALLET_JIZO_SET):
		specific_scene_rule = specific_scene_rule | rule_require_item_combo(("mallet", "jizo"))

	specific_scene_rule = specific_scene_rule | get_very_specific_scene_rules(used_day_id, used_scene_id)

	# Check if the Scene also appears in the No-Item set.
	# If it does, no items are required. Automatically set to True.
	if check_if_scene_in_set(used_day_id, used_scene_id, NORMAL_CLEAR_NO_ITEM_SET):
		specific_scene_rule = True_()

	return generic_scene_rule & specific_scene_rule

# Utils to check if a Scene exists in a Set from scene_clear.py files.
# If the Day ID matches any [0] of the tuple,
# and Scene ID appears in [1], said item is required for that scene.
# Day and Scene ID indexed from 1.
def check_if_scene_in_set(day_id: int, scene_id: int, given_set: tuple) -> bool:
	for day_scene_tuple in given_set:
		if day_id == day_scene_tuple[0]:
			if type(day_scene_tuple[1]) == tuple:
				return scene_id in day_scene_tuple[1]
			if type(day_scene_tuple[1]) == int:
				return scene_id == day_scene_tuple[1]
	return False

def get_day_any_scene_rules(day_id: int = 1):
	"""
	Function that retrieves a rule compiling all rules of all scenes within a Day.
	Equivalent to HasAny(). Day ID is indexed from 1.
	"""
	if not (0 <= day_id <= 10): return False_()

	day_total_rule = False_()
	for scene_id in range(CONST_DAY_SCENE_COUNT[day_id - 1]):
		day_total_rule = day_total_rule | get_scene_rule(day_id - 1, scene_id)

	return day_total_rule

def get_day_all_scene_rules(day_id: int = 1):
	"""
	Function that retrieves a rule compiling all rules of all scenes within a Day.
	Equivalent to Has(). Day ID is indexed from 1.
	"""
	if not (0 <= day_id <= 10): return False_()

	day_total_rule = True_()
	for scene_id in range(CONST_DAY_SCENE_COUNT[day_id - 1]):
		day_total_rule = day_total_rule & get_scene_rule(day_id - 1, scene_id)

	return day_total_rule

def rule_require_scene_count(scene_count: int = 0):
	"""
	Rule that checks how many scenes must be accessible.
	"""
	return Has(EVENT_ITEM_SCENE_UNLOCK_NAME, count=scene_count)

#
# SCENE CLEAR WITH SPECIFIC ITEM
#
def get_scene_item_clear_potential(day_id: int = 1, scene_id: int = 1):
	"""
	Function that returns which scene has the potential to clear with what item.
	Returns an empty set if it fails to find anything.
	Day and Scene ID are indexed from 1.
	"""
	if scene_id in RULE_TABLE_ITEM_SCENE[day_id - 1].keys():
		return RULE_TABLE_ITEM_SCENE[day_id - 1][scene_id]
	return tuple()

def get_scene_rule_per_item(day_id: int, scene_id: int, item_string_id: str):
	"""
	Retrieves a rule for a scene clear for only one specific item.
	Day ID and Scene ID are indexed from 1.
	"""
	# Example: 1-1 with Fabric item
	# 1. Get the standard Scene access rule
	# 2. Check if 1-1 exists in the Fabric set
	#    If yes, rule is updated to the Fabric as main.
	# 3. Go over the specific lookup table; these have written out what item clear can be gained
	#    from their special rule.
	# 4. If the item in question exists over there, |= that special rule in as well.
	# 5. If 1-1 exists in the No-Item set, automatically change the rule to True_().
	# 6. If 1-1 exists in the No-Item Doll Sub-item set, automatically change the rule to require Doll Sub-item.

	# Example: 1-1 Itemless
	# 1. Get the standard Scene access rule
	# 2. Jump to step 5

	scene_access_rule = rule_require_scene_access(
		day_id=day_id,
		scene_id=scene_id
	)
	# If it's a No-Item Clear, skip this. No-Item clears get checked at the final step.
	# Doll Sub scenes are treated the same as a No-Item clear, but with the Doll Sub-item requirement.
	specific_scene_rule = False_()
	if item_string_id != "none":
		if check_if_scene_in_set(day_id, scene_id, CONST_ITEM_SHORT_TO_CLEAR_SET[item_string_id]):
			specific_scene_rule = rule_require_one_main_item(item_string_id)

		match item_string_id:
			case "jizo":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_JIZO_DOLL_SET):
					specific_scene_rule = specific_scene_rule | rule_require_item_combo(("jizo", "doll"))
			case "lantern":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_LANTERN_DOLL_SET):
					specific_scene_rule = specific_scene_rule | rule_require_item_combo(("lantern", "doll"))
			case "mallet":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_MALLET_JIZO_SET):
					specific_scene_rule = specific_scene_rule | rule_require_item_combo(("mallet", "jizo"))

		scene_item_potential_set = tuple(get_scene_item_clear_potential(day_id, scene_id))

		if len(scene_item_potential_set) > 0:
			if item_string_id in scene_item_potential_set:
				specific_scene_rule = specific_scene_rule | get_very_specific_scene_rules(day_id, scene_id)

	if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_NO_ITEM_SET):
		specific_scene_rule = True_()
	if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_DOLL_SUB_SET):
		specific_scene_rule = rule_require_one_sub_item("doll")

	return scene_access_rule & specific_scene_rule

#
# NICKNAMES
#
def get_nickname_rule(nickname_id: int = 0):
	"""
	Retrieves a rule that applies to the given nickname. Indexed from 0.
	"""
	nickname_rule = False_()
	if 2 <= nickname_id < 8:  # 10-60 scene clears.
		nickname_rule = rule_require_generic_clear((nickname_id - 1) * 10)
	elif 14 <= nickname_id < 17:
		nickname_rule = rule_require_scene_count((nickname_id - 13) * 20)
	elif 17 <= nickname_id < 20:
		nickname_rule = rule_require_scene_count((nickname_id - 16) * 20)
	elif 20 <= nickname_id < 30:
		day_all_clear_id: int = nickname_id - 20
		nickname_rule = rule_require_day_clears(day_all_clear_id + 1, CONST_DAY_SCENE_COUNT[day_all_clear_id])
	elif 30 <= nickname_id < 70:
		if nickname_id < 40:  # 3 scenes
			used_id = nickname_id - 30
			clear_count = 3
		elif nickname_id < 50:  # 10 scenes
			used_id = nickname_id - 40
			clear_count = 10
		elif nickname_id < 60:  # 20 scenes
			used_id = nickname_id - 50
			clear_count = 20
		else:  # All 75 scenes
			used_id = nickname_id - 60
			clear_count = 75

		nickname_rule = rule_require_item_clears(used_id, clear_count)
	# Outlier cases that cannot be automated.
	else:
		match nickname_id:
			case 0:  # All scenes cleared
				nickname_rule = rule_require_generic_clear(75)
			case 1:  # 5 scene clears
				nickname_rule = rule_require_generic_clear(5)
			case 8:  # 8-1 clear
				nickname_rule = get_scene_rule(8 - 1, 1 - 1)
			case 9:  # Any Day 10 scene clear
				nickname_rule = get_day_any_scene_rules(10)
			case 10:  # 1-1 clear
				nickname_rule = get_scene_rule(1 - 1, 1 - 1)
			case 11:  # 3-1 clear
				nickname_rule = get_scene_rule(3 - 1, 1 - 1)
			case 12:  # 5-1 clear
				nickname_rule = get_scene_rule(5 - 1, 1 - 1)
			case 13:  # 6-1 clear
				nickname_rule = get_scene_rule(6 - 1, 1 - 1)

	return nickname_rule

#
# GOAL CONDITIONS
#
def get_all_day_clears(clear_count_per_day: int = 4):
	"""
	Rule that requires all Days having had a certain number of cleared scenes.
	Days that have less than the given number will adjust accordingly.
	"""
	goal_rule = False_()

	for day_id in range(10):
		true_clear_count = CONST_DAY_SCENE_COUNT[day_id]
		goal_rule = goal_rule | rule_require_day_clears(day_id + 1, clamp(clear_count_per_day, 0, true_clear_count))

	return goal_rule

def get_all_nickname_rules(nickname_count: int = 60):
	if nickname_count <= 0: return False_()

	nickname_rule = False_()
	for nick_id in range(nickname_count):
		nickname_rule = nickname_rule | get_nickname_rule(nick_id)

	return nickname_rule

def get_gold_hunt_rule(treasure_count: int = 1):
	return Has(CONST_TREASURE_ITEM_NAMES[0], count=treasure_count)


#
# STATIC LOOKUP TABLES
#
# Day ID starts at 0.
# Table for other item combinations that cannot be automated.
# Value is a rule.
RULE_TABLE_SCENE_SPECIFIC = [
	# Day 1
	{
		4: rule_require_one_sub_item("umbrella"),
		5: rule_require_one_sub_item("umbrella")
	},
	# Day 2
	{
		5: rule_require_item_combo(("yinyang", "doll"))
	},
	# Day 3
	{
		3: rule_require_item_combo(("mallet", "umbrella")),
		7: rule_require_item_combo(("yinyang", "jizo"))
	},
	# Day 4
	{
		2: rule_require_one_sub_item("jizo"),
		4: (rule_require_one_sub_item("umbrella") | rule_require_item_combo(("camera", "doll")))
	},
	# Day 5
	{
		3: (rule_require_one_main_item("lantern") & rule_require_specific_sub_items(["umbrella", "fabric", "jizo"])),
		4: rule_require_one_sub_item("umbrella"),
		5: (rule_require_one_main_item("fabric") & rule_require_specific_sub_items(["doll", "fabric", "jizo", "mallet"]))
	},
	# Day 6
	{
		2: rule_require_item_combo(("lantern", "fabric")),
		4: rule_require_item_combo(("mallet", "mallet")),
		6: rule_require_item_combo(("lantern", "mallet"))
	},
	# Day 7
	{},
	# Day 8
	{
		5: (rule_require_item_combo(("lantern", "umbrella")) |
			(rule_require_one_main_item("umbrella") & rule_require_specific_sub_items(["jizo", "umbrella", "mallet"])))
	},
	# Day 9
	{
		3: rule_require_item_combo(("umbrella", "doll")),
		7: rule_require_item_combo(("fabric", "doll"))
	},
	# Day 10
	{
		7: rule_require_item_combo(("bomb", "doll")),
		8: rule_require_item_combo(("bomb", "doll")),
		9: (rule_require_one_main_item("umbrella") & rule_require_specific_sub_items(["umbrella", "mallet"]))
	}
]

# Table for other item combinations that cannot be automated.
# Day ID starts at 0.
# Accounts for what items can be used to register for clears if a sub-item was consumed. (Mainly umbrella and jizo)
# Value is a set/tuple of Item String IDs. ONLY do For loops on them.
RULE_ALL_ITEM_NO_ITEMLESS: set[str] = set(CONST_ITEM_SHORT_TO_ID.keys())
if "none" in RULE_ALL_ITEM_NO_ITEMLESS: RULE_ALL_ITEM_NO_ITEMLESS.remove("none")
RULE_TABLE_ITEM_SCENE = [
	# Day 1
	{
		4: RULE_ALL_ITEM_NO_ITEMLESS,
		5: RULE_ALL_ITEM_NO_ITEMLESS
	},
	# Day 2
	{
		5: ("yinyang")
	},
	# Day 3
	{
		3: ("mallet"),
		7: ("yinyang")
	},
	# Day 4
	{
		2: RULE_ALL_ITEM_NO_ITEMLESS,
		4: RULE_ALL_ITEM_NO_ITEMLESS
	},
	# Day 5
	{
		3: ("lantern"),
		4: RULE_ALL_ITEM_NO_ITEMLESS,
		5: ("fabric")
	},
	# Day 6
	{
		2: ("lantern"),
		4: ("mallet"),
		6: ("lantern")
	},
	# Day 7
	{},
	# Day 8
	{
		5: ("lantern", "umbrella")
	},
	# Day 9
	{
		3: ("umbrella"),
		7: ("fabric")
	},
	# Day 10
	{
		7: ("bomb"),
		8: ("bomb"),
		9: ("umbrella")
	}
]