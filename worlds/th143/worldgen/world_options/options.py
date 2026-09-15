from dataclasses import dataclass

from Options import PerGameCommonOptions, OptionGroup, ProgressionBalancing, Accessibility, \
	StartInventoryPool
from .options_classes import *

@dataclass()
class ISCDataclass(PerGameCommonOptions):
	# Standard
	skill_difficulty: SkillDifficulty
	trap_chance: TrapChance
	trap_blacklist: TrapBlacklist
	death_link: DeathLink
	death_link_amnesty: DeathLinkAmnesty
	death_link_anti: InvincAgainstDeathLink
	completion_type: CompletionType
	start_inventory_from_pool: StartInventoryPool
	# Gold Rush
	treasure_percent: TreasurePercent
	treasure_required: TreasureRequired
	# Progression
	progressive_day: ProgressiveDay
	progressive_scene: ProgressiveScene
	starting_day: StartingDay
	starting_day_random_range: StartingDayRandomRange
	valid_starting_days: ValidStartingDays
	# Cheat Items
	item_upgrade_progress: ItemUpgradeProgression
	item_upgrade_separate: ItemUpgradeSeparate
	item_upgrade_remove_cap: ItemUpgradeRemoveCap
	subitem_slot_unlock: SubitemSlotUnlock
	subitem_individual: SubitemIndividual
	scene_skip_count: SceneSkipCount
	useless_filler: UselessFillerAllowed
	# Logic/Locations
	playtime_mult: PlaytimeMultiplier
	include_music_checks: IncludeMusicRoomChecks
	include_itemless_logic: IncludeItemlessLogic
	include_item_clears: IncludeItemClears
	include_hidden_nicknames: IncludeHiddenAchievements

option_groups = [
	OptionGroup(
		"Game Options", [
			ProgressionBalancing,
			Accessibility,
			CompletionType,
			SkillDifficulty,
			TrapChance,
			TrapBlacklist,
			DeathLink,
			DeathLinkAmnesty,
			InvincAgainstDeathLink
		]
	),
	OptionGroup(
		"Treasure Hunt Options", [
			TreasurePercent,
			TreasureRequired
		]
	),
	OptionGroup(
		"Scene Progression Options", [
			ProgressiveDay,
			ProgressiveScene,
			StartingDay,
			StartingDayRandomRange,
			ValidStartingDays
		]
	),
	OptionGroup(
		"Item Generation Options", [
			ItemUpgradeProgression,
			ItemUpgradeSeparate,
			ItemUpgradeRemoveCap,
			SubitemSlotUnlock,
			SubitemIndividual,
			SceneSkipCount,
			UselessFillerAllowed
		]
	),
	OptionGroup(
		"Extra Logic Options", [
			PlaytimeMultiplier,
			IncludeMusicRoomChecks,
			IncludeItemlessLogic,
			IncludeItemClears,
			IncludeHiddenAchievements
		]
	)
]

option_presets = {
	"Normal All Items": {
		"skill_difficulty": 1,
		"trap_chance": 10,
		"death_link": False,
		"completion_type": 2,

		"progressive_day": False,
		"progressive_scene": 2,
		"starting_day": 0,

		"item_upgrade_progress": 0,
		"item_upgrade_separate": False,
		"subitem_slot_unlock": True,
		"subitem_individual": True,
		"scene_skip_count": 20,
		"useless_filler": True,

		"include_music_checks": True,
		"include_itemless_logic": False,
		"include_item_clears": False,
		"include_hidden_nicknames": False
	}
}