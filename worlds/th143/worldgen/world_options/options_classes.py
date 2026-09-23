from Options import Range, Choice, T, DefaultOnToggle, OptionSet, Toggle, ItemSet
from ...variables.location_item_name import CONST_DAY_TO_ID, CONST_TEMP_PREFIX, CONST_FILLER_NAME


#
# DEFAULT OPTIONS
#
class SkillDifficulty(Choice):
	"""
	What level of skill that logic expects of the player in order to clear all scenes.
	(All difficulties are Normal at the moment.)
	"""
	display_name = "Skill Difficulty"

	option_normal = 1
	option_hard = 2
	option_lunatic = 3

	default = option_normal

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_normal:
			return "Normal Mode"
		elif value == cls.option_hard:
			return "Hard Mode"
		elif value == cls.option_lunatic:
			return "Lunatic Mode"
		return super().get_option_name(value)

class TrapChance(Range):
	"""
	Percentage chance that any given filler Item will be replaced by a trap item.
	"""
	display_name = "Trap Chance"

	range_start = 0
	range_end = 100
	default = 10

class TrapBlacklist(ItemSet):
	"""
	Which Trap items will not be generated if Trap Chance is higher than 0.
	Remove any of these entries if you want those traps to appear.
	"""
	from worlds.th143.worldgen.items import get_items_by_category, CATEGORY_TRAP

	display_name = "Trap Blacklist"

	valid_keys = get_items_by_category(CATEGORY_TRAP).keys()
	default = [
		CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_down"],
		CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_down2"]
	]

class DeathLink(Toggle):
	"""
	Upon failing a Scene, everyone who enabled Death Link dies.
	If someone else dies, the game will attempt to kill you as if you got hit by a bullet.
	"""
	display_name = "Death Link"
	rich_text_doc = True

class DeathLinkAmnesty(Range):
	"""
	Only applicable if Death Link is enabled.
	How many deaths are allowed before a Death Link is sent.
	"""
	display_name = "Death Link Amnesty"

	range_start = 0
	range_end = 30
	default = 0

class InvincAgainstDeathLink(DefaultOnToggle):
	"""
	Only applicable if Death Link is enabled.
	Whether invincibility will stave off an incoming Death Link.
	"""
	display_name = "Anti-Death Link Invincibility"

class CompletionType(Choice):
	"""
	A goal to reach.

	0 - Clear 4 Scenes from Day 10.
	1 - Clear all Scenes from Day 10.
	2 - Clear 4 Scenes from all Days.
	3 - Clear all Scenes from all Days.
	4 - Find all Nicknames, excluding hidden ones.
	5 - Find all Nicknames, INCLUDING hidden ones. Reverts to 4 if Include Hidden Nicknames is disabled.
	6 - Find a certain number of Koban Coins scattered throughout the world.
	"""
	display_name = "Completion Goal"

	option_day_10_4_scenes = 0
	option_day_10_all_scenes = 1
	option_all_days_4_scenes = 2
	option_all_days_all_scenes = 3
	option_all_achievements_exclude = 4
	option_all_achievements_true = 5
	option_gold_rush = 6

	default = option_day_10_4_scenes

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_day_10_4_scenes:
			return "Clear 4 Scenes on Day 10"
		elif value == cls.option_day_10_all_scenes:
			return "Clear all Scenes on Day 10"
		elif value == cls.option_all_days_4_scenes:
			return "Clear 4 Scenes on all Days"
		elif value == cls.option_all_days_all_scenes:
			return "Clear all Scenes on all Days"
		elif value == cls.option_all_achievements_exclude:
			return "Find all Nicknames (Excludes Hidden Nicknames)"
		elif value == cls.option_all_achievements_true:
			return "Find all Nicknames/Clear everything"
		elif value == cls.option_gold_rush:
			return "Gold Rush (Treasure Hunt)"
		return super().get_option_name(value)

#
# TREASURE HUNT / GOLD RUSH SETTINGS
#
class TreasureRequired(Range):
	"""
	Only applicable if Completion Goal is set to Gold Rush (Treasure Hunt).
	How many % of the Treasure items there are in the world should be required for goal?
	"""
	display_name = "Gold Rush Requirement"

	range_start = 15
	range_end = 100
	default = 15

class TreasurePercent(Range):
	"""
	Only applicable if Completion Goal is set to Gold Rush (Treasure Hunt).
	How many % of the Filler pool should be replaced with Treasure items?
	"""
	display_name = "Gold Rush Filler Percentage"

	range_start = 5
	range_end = 100
	default = 15

#
# PROGRESSION
#
class ProgressiveDay(DefaultOnToggle):
	"""
	Whether the game will begin with all Days unlocked or not.
	If enabled, each Day must be progressively unlocked up to Day 10.
	Otherwise, all Days are unlocked from the start.
	"""
	display_name = "Progressive Day"

class ProgressiveScene(Choice):
	"""
	How Scene access should be in the game.

	0. Original/Vanilla - Day 3, 5, 6, and 8 will be locked to Scene 1 until an item is gained to unlock the rest.
	1. Vanilla + Day 1 - Same as the above, but Day 1 is included.
	2. First Scene Restriction - All Days require 2 progressive items to fully unlock their Scenes.
	3. Gradual Scene Unlock - All Days require many of their respective Scene unlocks to slowly access more Scenes.
	4. Instant Scene Unlock - All Days can be fully unlocked with only one of their respective Scene unlock.
	"""
	display_name = "Progressive Scene"

	option_original_vanilla = 0
	option_vanilla_plus_one = 1
	option_first_scene_only = 2
	option_gradual_unlock = 3
	option_full_unlock = 4

	default = option_original_vanilla

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_original_vanilla:
			return "Original/Vanilla"
		elif value == cls.option_vanilla_plus_one:
			return "Vanilla + Day 1"
		elif value == cls.option_first_scene_only:
			return "First Scene Restriction"
		elif value == cls.option_gradual_unlock:
			return "Gradual Scene Unlock"
		elif value == cls.option_full_unlock:
			return "Instant Scene Unlock"
		return super().get_option_name(value)

class StartingDay(Choice):
	"""
	Which Day to begin with.
	If Progressive Day is enabled, all previous Days will also be unlocked.
	Otherwise, only Scene 1 of the selected Day will be unlocked at minimum.
	"""
	display_name = "Starting Day"

	option_day_1 = 0
	option_day_2 = 1
	option_day_3 = 2
	option_day_4 = 3
	option_day_5 = 4
	option_day_6 = 5
	option_day_7 = 6
	option_day_8 = 7
	option_day_9 = 8
	option_day_10 = 9
	option_random_day = 10

	default = option_day_1

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_day_1:
			return "Day 1"
		elif value == cls.option_day_2:
			return "Day 2"
		elif value == cls.option_day_3:
			return "Day 3"
		elif value == cls.option_day_4:
			return "Day 4"
		elif value == cls.option_day_5:
			return "Day 5"
		elif value == cls.option_day_6:
			return "Day 6"
		elif value == cls.option_day_7:
			return "Day 7"
		elif value == cls.option_day_8:
			return "Day 8"
		elif value == cls.option_day_9:
			return "Day 9"
		elif value == cls.option_day_10:
			return "Final Day"
		elif value == cls.option_random_day:
			return "Randomized Start"
		return super().get_option_name(value)

class StartingDayRandomRange(Range):
	"""
	Only applicable if Starting Day is set to Randomized Start.
	If Progressive Scene is enabled, this option is locked to 1.
	Affects how many Days the player will begin with at random.
	Minimum of 1, maximum of 10.
	"""
	display_name = "Randomized Start: Starting Days"

	range_start = 1
	range_end = 10
	default = 3

class ValidStartingDays(OptionSet):
	"""
	Only applicable if Starting Day is set to Randomized Start.
	Affects which Day will be in the randomized starting pool.
	If there are none, it will be assumed that all Days are eligible.
	"""
	display_name = "Randomized Start: Valid Days"
	valid_keys = CONST_DAY_TO_ID.keys()
	default = valid_keys

class PlaytimeMultiplier(Choice):
	"""
	Determines the multiplier for the playtime needed to attain the playtime nicknames.
	"""
	display_name = "Playtime Requirement Multiplier"

	option_vanilla = 0
	option_half = 1
	option_fifth = 2

	default = option_half

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_vanilla:
			return "Vanilla (x1.0)"
		elif value == cls.option_half:
			return "Halved (x0.5)"
		elif value == cls.option_fifth:
			return "Fast (x0.2)"
		return super().get_option_name(value)

#
# ITEMS
#
class ItemUpgradeProgression(Choice):
	"""
	Determines how item use count and stat should be handled.
	(Currently fixed to Vanilla; will change in the future.)

	0. Vanilla - Exactly as in the original game.
	1. Vanilla Max+ - Items can go beyond Max.
	2. Rebalanced - Item levels will be rebalanced for a different experience.
	"""
	display_name = "Cheat Item Progression: Stat Level Up Configuration"

	option_vanilla = 0
	option_vanilla_plus = 1
	option_custom_system = 2

	default = option_vanilla

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_vanilla:
			return "Vanilla"
		elif value == cls.option_vanilla_plus:
			return "Vanilla Max+"
		elif value == cls.option_custom_system:
			return "Rebalanced"
		return super().get_option_name(value)

class ItemUpgradeSeparate(Toggle):
	"""
	If enabled, Cheat Item use count and stats will require separate items each.
	"""
	display_name = "Cheat Item Progression: Separate Upgrades"

class ItemUpgradeRemoveCap(Choice):
	"""
	Only applicable if Cheat Item Progression is Max+ Levels or Rebalanced, and Separate Upgrades is disabled.
	Configures whether the player would require a Remove Level Cap item to increase item level past the vanilla maximum.

	0. Disabled - Has no vanilla level cap in place.
	1. Global - Requires only 1 Remove Level Cap item to do so for all items.
	2. Individual - Each item requires their respective Remove Level Cap item.
	"""
	display_name = "Cheat Item Progression: Level Cap Removal"

	option_none = 0
	option_global = 1
	option_individual = 2

	default = option_none

	@classmethod
	def get_option_name(cls, value: T) -> str:
		if value == cls.option_none:
			return "Disabled"
		elif value == cls.option_global:
			return "Global"
		elif value == cls.option_individual:
			return "Individual"
		return super().get_option_name(value)

class SubitemSlotUnlock(DefaultOnToggle):
	"""
	If enabled, unlocking the Sub-item slot will require a specific item.
	Otherwise, it will not be necessary to use Sub-items.
	"""
	display_name = "Sub-item Progression: Itemized Equip Slot"

class SubitemIndividual(Toggle):
	"""
	If enabled, each Sub-item will require their own specific item to be available for use.
	Otherwise, as soon as the Sub-item slot is unlocked, all Sub-items will be available.
	"""
	display_name = "Sub-item Progression: Itemized Individual Sub-items"

#
# FILLER ITEM SETTINGS
#
class SceneSkipCount(Range):
	"""
	How many Scene Skip items can appear in the item pool?
	"""
	display_name = "Scene Skip Count"

	range_start = 0
	range_end = 70
	default = 6

class UselessFillerAllowed(DefaultOnToggle):
	"""
	Whether useless Filler items that do exactly nothing will be part of the Filler item pool.
	"""
	display_name = "Allow Useless Filler"

#
# LOGIC/LOCATIONS
#
class IncludeMusicRoomChecks(DefaultOnToggle):
	"""
	Whether Music Room unlocks also count as Locations.
	If enabled, this adds 8 more Locations.
	"""
	display_name = "Include Music Room Locations"

class IncludeItemlessLogic(Toggle):
	"""
	Almost all Scenes in the game are possible to clear without using Items. However, that is excessively difficult.
	Disabling this option means that only reasonably easy No-Item Scenes would be accounted for in logic.
	(Does nothing at the moment; treated as disabled.)
	"""
	display_name = "Include Difficult No-Item Logic"

class IncludeItemClears(Toggle):
	"""
	If enabled, this adds 750 more Locations to be checked.
	These Locations are for clearing Scenes using specific items as well as without items.
	It is recommended to leave it disabled unless you are prepared for a brutal no-item run.
	"""
	display_name = "Include Item-specific Scene Clears"

class IncludeHiddenAchievements(Toggle):
	"""
	If enabled, this adds 10 more Locations to be checked.
	These Locations are for the last row of Nicknames (61-70), which are hidden at the start.
	These are Locations for clearing all Scenes using specific items as well as without items.
	It is recommended to leave it disabled unless you are prepared for a brutal no-item run.
	"""
	display_name = "Include Hidden Nicknames"