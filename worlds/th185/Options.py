from Options import *
from .variables.boss_and_stage import TUTORIAL_NAME_FULL, STAGE1_NAME_FULL, STAGE2_NAME_FULL, STAGE3_NAME_FULL, STAGE4_NAME_FULL, \
    STAGE5_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL, CHALLENGE_NAME_FULL, ONCE_ITEM_TAG
from .variables.card_const import YACHIE_CARD_NAME, KAGUYA_CARD_NAME, TAKANE_STORY_CARD_NAME, JUNKO_CARD_NAME


class StartingMarket(Choice):
    """
    Choose which stage to have unlocked at the start of the game.

    If Progressive Markets is enabled:
    - Unlock items for stages preceding the Starting Market will not appear.
    - Any stages preceding the Starting Market will be unlocked.
    """

    display_name = "Starting Market"

    option_Tutorial = 0
    option_Stage1 = 1
    option_Stage2 = 2
    option_Stage3 = 3
    option_Stage4 = 4
    option_Stage5 = 5
    option_Stage6 = 6
    option_Stage7 = 7
    option_Challenge = 8

    default = option_Tutorial

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_Tutorial:
            return TUTORIAL_NAME_FULL
        elif value == cls.option_Stage1:
            return STAGE1_NAME_FULL
        elif value == cls.option_Stage2:
            return STAGE2_NAME_FULL
        elif value == cls.option_Stage3:
            return STAGE3_NAME_FULL
        elif value == cls.option_Stage4:
            return STAGE4_NAME_FULL
        elif value == cls.option_Stage5:
            return STAGE5_NAME_FULL
        elif value == cls.option_Stage6:
            return STAGE6_NAME_FULL
        elif value == cls.option_Stage7:
            return ENDSTAGE_NAME_FULL
        elif value == cls.option_Challenge:
            return CHALLENGE_NAME_FULL
        return super().get_option_name(value)


class ProgressiveStages(DefaultOnToggle):
    """
    Stages will be unlocked in order as the game progresses.
    """

    display_name = "Progressive Market"


class StageBossLocations(Choice):
    """
    Whether boss encounters and defeats will count as locations, and whether stage clears will count as locations.
    """

    option_boss_only = 0
    option_stage_only = 1
    option_full = 2

    default = option_boss_only

    display_name = "Boss and Stage Locations"

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_boss_only:
            return "Boss Locations Only"
        if value == cls.option_stage_only:
            return "Stage Clear Locations Only"
        if value == cls.option_full:
            return "Full Boss and Stage Clear Locations"
        return super().get_option_name(value)


class ProgressiveLoadout(Choice):
    """
    Whether starting card slots and equip cost will be upgraded according to the number of bosses defeated or via items received.
    The game begins with 1 starting card slot and 100% equip cost.

    1. Disabled - Slots and cost will be unlocked according to the number of bosses defeated (vanilla).
    2. Simultaneous - Both slots and cost will be upgraded at the same time.
    3. Separate - Slots and cost will only be upgraded with the appropriate items received.
    """

    option_none = 0
    option_together = 1
    option_separate = 2

    default = option_none

    display_name = "Itemize Equipment Upgrades"

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_none:
            return "Disabled/Vanilla"
        if value == cls.option_together:
            return "Simultaneous Equipment Upgrades"
        if value == cls.option_separate:
            return "Separate Equipment Upgrades"
        return super().get_option_name(value)


class ProgressiveLoadoutCount(Range):
    """
    Only used if "Itemize Equipment Upgrades" is set to Simultaneous.
    This will determine how many of them will be in the item pool.
    Minimum of +6 items because of one of the Achievements.
    Can technically go up to +33, but it is recommended to only go up to +15 at most.
    """
    range_start = 6
    range_end = 33
    default = 6
    alias_Max = 15

    display_name = "Simultaneous - Equipment Upgrades Count"


class ProgressiveSlotCount(Range):
    """
    Only used if "Itemize Equipment Upgrades" is set to Separate.
    This determines how many starting card slot upgrades will be in the item pool.
    Minimum of +6 slots because of one of the Achievements.
    Can technically go up to +33, but it is recommended to only go up to +15 at most.
    """
    range_start = 6
    range_end = 33
    default = 6
    alias_Max = 15

    display_name = "Separate - Starting Card Slot Upgrades Count"


class ProgressiveCostCount(Range):
    """
    Only used if "Itemize Equipment Upgrades" is set to Separate.
    This will determine how many equip cost upgrades will be in the item pool.
    Equip cost maxes out at +900%, and each upgrade is worth 50%.
    """
    range_start = 5
    range_end = 18
    default = 6

    display_name = "Separate - Equip Cost Upgrades Count"


class AntiGrindingToggle(Toggle):
    """
    Toggles whether generation logic should consider anti-grinding placements.
    """

    display_name = "Anti-Grinding Item Toggle"


class AntiGrindingItemPlacements(ItemSet):
    """
    Which items should be prioritized for placement during early game to reduce grinding as much as possible.
    Four cards and 1000 Funds are on the list by default, but you can choose to remove them.
    """

    display_name = "Anti-Grinding Item Placements"
    valid_keys = [
        YACHIE_CARD_NAME,
        KAGUYA_CARD_NAME,
        TAKANE_STORY_CARD_NAME,
        JUNKO_CARD_NAME,
        "+1000 Funds"
    ]
    default = valid_keys


class DisableChallengeLogic(DefaultOnToggle):
    """
    Generation logic will consider Challenge Market inaccessible if all other stages have not been unlocked yet.
    Disable this option to turn off the above handicap.
    """

    display_name = "Lock Challenge Market in Logic"


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
    from .Items import get_items_by_category, CATEGORY_TRAP
    valid_keys = get_items_by_category(CATEGORY_TRAP).keys()
    default = [
        ONCE_ITEM_TAG + "Funds Reset Trap",
        ONCE_ITEM_TAG + "Bullet Money Reset Trap",
        ONCE_ITEM_TAG + "20% Shot Attack Trap",
        ONCE_ITEM_TAG + "0% Magic Circle Attack Trap",
        ONCE_ITEM_TAG + "1000% Magic Circle Duration Trap",
        ONCE_ITEM_TAG + "Shot Power Reset Trap"
    ]
    display_name = "Trap Blacklist"


class TrapDurations(OptionCounter):
    """
    How much time should any of the Temporary traps last (in seconds, max 900).
    If not set, the game will assume default values as follows:

    Extreme Speed Trap/"aya_speed" - 5 seconds
    Magic Circle Disable Trap/"circle_disable" - 15 seconds
    Freeze Trap/"freeze" - 3 seconds
    Powerless Shot Trap/"powerless" - 6 seconds
    """

    display_name = "Temporary Trap Durations"
    valid_keys = [
        "aya_speed", "circle_disable", "freeze", "powerless"
    ]
    min = 2
    max = 900
    default = {
        "aya_speed": 5,
        "circle_disable": 15,
        "freeze": 3,
        "powerless": 6,
    }


class LowSkillLogic(Choice):
    """
    Whether the generation logic should include certain Ability Cards as compulsory before challenging late-game stages.

    0. Disabled.
    1. Stage 4 requires only 2 of them, stage 5 requires 4, etc.
    2. All late-game stages logically require all cards below.

    * 4th-6th Market + Challenge Market:
    Life Explosion Elixir, Princess Kaguya's Secret Stash, Soot-covered Uchiwa,
    Esteemed Authority, Gluttonous Centipede, and Money Is The Best Lawyer In Hell.
    * End of Market:
    Life Explosion Elixir, Esteemed Authority
    * Takane: + Lucky Cat with Good Business Skills
    * Nitori: + 1 card loadout slot progression
    """

    display_name = "Recommended Loadout in Logic"

    option_none = 0
    option_scale = 1
    option_full = 2

    default = option_scale

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_none:
            return "Disabled"
        if value == cls.option_scale:
            return "Scale According to Stage"
        if value == cls.option_full:
            return "Enforce Full Loadout"
        return super().get_option_name(value)


class LowSkillStats(Toggle):
    """
    Whether generation logic should also consider placing itemized equipment upgrades before late-game stages.
    This only works if "Itemize Equipment Upgrades" and "Recommended Loadout in Logic" are enabled.
    This will scale based on "Recommended Loadout in Logic".
    """

    display_name = "Recommended Equipment Upgrades in Logic"


class IncludeGameplayFiller(DefaultOnToggle):
    """
    Whether filler items that are not Funds or Bullet Money will appear during generation.
    Also affects Traps.
    """

    display_name = "Include Non-Money Filler"


class DeathLinkTrigger(Choice):
    """
    Determines when a Death Link would be sent. Only takes effect if Death Link is enabled.
    Can be temporarily changed during gameplay.

    0. Upon losing a life. This means Life Explosion Elixir will also trigger Death Link.
    1. Upon failing a stage attempt. All lives must be lost before this triggers.
    """

    display_name = "Death Link Trigger"

    option_life = 0
    option_stage = 1

    default = option_life

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_life:
            return "Upon losing a life"
        if value == cls.option_stage:
            return "Upon failing a stage attempt"
        return super().get_option_name(value)

class InvincAgainstDeathLink(DefaultOnToggle):
    """
    Determines whether invincibility can protect against incoming Death Links.
    """

    display_name = "Anti-Death Link Invincibility"


class EnergyLink(Toggle):
    """
    Allows usage of the EnergyLink pool.
    Funds can be deposited and withdrawn at a certain exchange rate.
    However, undeposited and withdrawn Funds will not be automatically saved.
    """

    display_name = "Energy Link"


class EnergyLinkBulletMoney(Toggle):
    """
    If enabled, EnergyLink exchanges permit exchanging energy for Bullet Money as well.
    Conversion rates for Bullet Money differ from that for Funds.
    Bullet Money cannot be deposited nor withdrawn outside of stages.
    """

    display_name = "Energy Link Bullet Money Exchanges"


class MusicRoomChecks(Toggle):
    """
    Whether soundtrack unlocks in the Music Room also counts as checks.
    """

    display_name = "Enable Music Room Checks"


class AchieveChecks(Toggle):
    """
    Whether Achievements also counts as checks.
    """

    display_name = "Enable Achievement Checks"


class CompletionType(Choice):
    """
    A goal to reach.

    1. Full Story Clear - Defeat Chimata Tenkyuu, Nitori Kawashiro, Takane Yamashiro.
    2. Minimum Story Clear - Defeat Takane Yamashiro.
    3. All Ability Cards Owned.
    4. All Bosses Defeated - Challenge Market does not count.
    5. Challenge Market Clear.
    6. Clear everything except Challenge Market.
    7. Clear everything.
    8. Dragon Gem Hunt - Collect a certain number of Dragon Gem items randomly placed throughout the game.
    """

    display_name = "Completion Goal"

    option_full = 0
    option_min = 1
    option_cards = 2
    option_bosses = 3
    option_challenge = 4
    option_all = 5
    option_true_all = 6
    option_dragon_gems = 7

    default = option_full

    @classmethod
    def get_option_name(cls, value: T) -> str:
        if value == cls.option_full:
            return "Full Story Clear"
        elif value == cls.option_min:
            return "Minimum Story Clear"
        elif value == cls.option_cards:
            return "All Ability Cards Owned"
        elif value == cls.option_bosses:
            return "All Bosses Defeated"
        elif value == cls.option_challenge:
            return "Challenge Market Clear"
        elif value == cls.option_all:
            return "Clear everything (Except Challenge Market)"
        elif value == cls.option_true_all:
            return "Clear everything"
        elif value == cls.option_dragon_gems:
            return "Dragon Gem Hunt"
        return super().get_option_name(value)


class DragonGemRequirement(Range):
    """
    Only effective if the Completion Type is set to Dragon Gem Hunt.
    This will determine how many Dragon Gem items are required for goal.
    If there are not enough locations for the required count, the count will be adjusted accordingly.
    """
    range_start = 1
    range_end = 100
    default = 30

    display_name = "Dragon Gems Required"


class DragonGemAmount(Range):
    """
    Only effective if the Completion Type is set to Dragon Gem Hunt.
    This will determine how many Dragon Gem items would be in the item pool.
    If this number is less than the victory condition number,
    the number in the item pool will be randomized with a minimum the same as the victory condition.
    """
    range_start = 1
    range_end = 100
    default = 60

    display_name = "Dragon Gems in Pool"


class PermaUpgradeToggle(Toggle):
    """
    Whether items for permanently upgrading player initial stats (starting lives, starting shot attack, etc.) will appear.
    These permanent upgrades were never part of the original game, and will not be required for progression.
    However, they will be prioritized for filler before other filler items can be placed (e.g. Funds filler, one-time Shot Attack bonuses).
    """

    display_name = "Allow Permanent Player Upgrades"


class PermaLifeCount(Range):
    """
    How many upgrades for additional starting lives? Cannot exceed 3 upgrades (4 starting lives).
    Note that you begin with 1 life by default in every stage.
    """
    range_start = 0
    range_end = 3
    default = range_start

    display_name = "Starting Upgrades: Lives"


class PermaBulletMoney(Range):
    """
    How many upgrades for additional starting Bullet Money? Each upgrade is worth 70 Bullet Money.
    Note that you begin with 0 Bullet Money by default in every stage.
    """
    range_start = 0
    range_end = 8
    default = range_start

    display_name = "Starting Upgrades: Bullet Money (70 Bullet Money/upgrade)"


class PermaShotPower(Range):
    """
    How many upgrades for additional starting Power? Cannot exceed 3 upgrades (4 starting Power).
    Note that you begin with 1 Power by default in every stage.
    """
    range_start = 0
    range_end = 3
    default = range_start

    display_name = "Starting Upgrades: Power"


class PermaShotStrength(Range):
    """
    How many upgrades for additional starting shot attack? Each upgrade is worth 5%.
    Note that you begin with 100% shot attack by default in every stage.
    """
    range_start = 0
    range_end = 8
    default = range_start

    display_name = "Starting Upgrades: Shot Attack (5%/upgrade)"


class PermaMagicStrength(Range):
    """
    How many upgrades for additional starting magic circle strength? Each upgrade is worth 5%.
    Note that you begin with 100% magic circle strength by default in every stage.
    """
    range_start = 0
    range_end = 10
    default = range_start

    display_name = "Starting Upgrades: Magic Circle Attack (5%/upgrade)"


@dataclass()
class TouhouHBMDataclass(PerGameCommonOptions):
    anti_grinding_toggle: AntiGrindingToggle
    anti_grinding_placements: AntiGrindingItemPlacements
    starting_market: StartingMarket
    progressive_stages: ProgressiveStages
    progressive_loadout: ProgressiveLoadout
    progressive_loadout_count: ProgressiveLoadoutCount
    progressive_slot_count: ProgressiveSlotCount
    progressive_cost_count: ProgressiveCostCount
    stage_boss_locations: StageBossLocations
    disable_challenge_logic: DisableChallengeLogic
    completion_type: CompletionType
    trap_chance: TrapChance
    trap_blacklist: TrapBlacklist
    trap_durations: TrapDurations
    low_skill_logic: LowSkillLogic
    low_skill_stats: LowSkillStats
    include_gameplay_filler: IncludeGameplayFiller
    dragon_gems_condition: DragonGemRequirement
    dragon_gems_pool: DragonGemAmount
    death_link: DeathLink
    death_link_trigger: DeathLinkTrigger
    death_link_invincibility: InvincAgainstDeathLink
    energy_link: EnergyLink
    energy_link_bullet_money: EnergyLinkBulletMoney
    music_room_checks: MusicRoomChecks
    achievement_checks: AchieveChecks
    start_inventory_from_pool: StartInventoryPool
    perma_upgrade_toggle: PermaUpgradeToggle
    perma_upgrade_life: PermaLifeCount
    perma_upgrade_bm: PermaBulletMoney
    perma_upgrade_power: PermaShotPower
    perma_upgrade_atk: PermaShotStrength
    perma_upgrade_magic_atk: PermaMagicStrength


option_groups = [
    OptionGroup(
        "Game Options", [
            ProgressionBalancing,
            Accessibility,
            CompletionType,
            TrapChance,
            TrapBlacklist,
            TrapDurations,
            IncludeGameplayFiller
        ]
    ),
    OptionGroup(
        "Death Link & Energy Link Options", [
            DeathLink,
            DeathLinkTrigger,
            InvincAgainstDeathLink,
            EnergyLink,
            EnergyLinkBulletMoney
        ]
    ),
    OptionGroup(
        "Generation Options", [
            StartingMarket,
            StageBossLocations,
            ProgressiveStages,
            MusicRoomChecks,
            AchieveChecks
        ]
    ),
    OptionGroup(
        "Equipment Upgrade Options", [
            ProgressiveLoadout,
            ProgressiveLoadoutCount,
            ProgressiveSlotCount,
            ProgressiveCostCount
        ]
    ),
    OptionGroup(
        "Gameplay Handicap Options", [
            AntiGrindingToggle,
            AntiGrindingItemPlacements,
            PermaUpgradeToggle,
            PermaLifeCount,
            PermaBulletMoney,
            PermaShotPower,
            PermaShotStrength,
            PermaMagicStrength
        ]
    ),
    OptionGroup(
        "Logic Handicap Options", [
            DisableChallengeLogic,
            LowSkillLogic,
            LowSkillStats
        ]
    ),
    OptionGroup(
        "Dragon Gem Hunt Options", [
            DragonGemRequirement,
            DragonGemAmount
        ]
    )
]

option_presets = {
    "Easy": {
        "completion_type": 1,
        "trap_chance": 10,
        "include_gameplay_filler": False,
        "death_link": False,
        "energy_link": False,
        "starting_market": 0,
        "progressive_stages": True,
        "stage_boss_locations": 1,
        "progressive_loadout": 0,
        "perma_upgrade_toggle": True,
        "perma_upgrade_life": 3,
        "perma_upgrade_bm": 8,
        "perma_upgrade_power": 3,
        "perma_upgrade_atk": 8,
        "perma_upgrade_magic_atk": 8,
        "disable_challenge_logic": True,
        "low_skill_logic": True
    },
    "Overdrive": {
        "progression_balancing": 99,
        "accessibility": 2,
        "completion_type": 6,
        "trap_chance": 100,
        "include_gameplay_filler": True,
        "trap_blacklist": [],
        "death_link": True,
        "death_link_invincibility": False,
        "starting_market": 8,
        "progressive_stages": False,
        "stage_boss_locations": 2,
        "music_room_checks": True,
        "achievement_checks": True,
        "progressive_loadout": 2,
        "progressive_cost_count": 12,
        "progressive_slot_count": 33,
        "anti_grinding_toggle": True,
        "anti_grinding_placements": [
            YACHIE_CARD_NAME,
            TAKANE_STORY_CARD_NAME,
        ],
        "perma_upgrade_toggle": True,
        "perma_upgrade_life": 3,
        "perma_upgrade_bm": 8,
        "perma_upgrade_power": 3,
        "perma_upgrade_atk": 8,
        "perma_upgrade_magic_atk": 8,
        "disable_challenge_logic": False,
        "low_skill_logic": False,
        "low_skill_stats": False
    }
}
