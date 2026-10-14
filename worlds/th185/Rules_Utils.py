# Utils specifically for generation rules.
from rule_builder.options import OptionFilter
from rule_builder.rules import HasAll, HasFromListUnique, True_, False_, Has, HasAny, HasAllCounts
from .Options import CompletionType, ProgressiveStages, LowSkillLogic, ProgressiveLoadout, DisableChallengeLogic, \
    LowSkillStats
from .Tools import get_progress_item_requirement, clamp, get_card_location_name_str, duplicate_list
from .variables.card_const import *

# commonly used stage lists
STANDARD_STAGE_LIST = duplicate_list(STAGE_NAME_LIST)
if TUTORIAL_NAME_FULL in STANDARD_STAGE_LIST: STANDARD_STAGE_LIST.remove(TUTORIAL_NAME_FULL)
if ENDSTAGE_NAME_FULL in STANDARD_STAGE_LIST: STANDARD_STAGE_LIST.remove(ENDSTAGE_NAME_FULL)
if CHALLENGE_NAME_FULL in STANDARD_STAGE_LIST: STANDARD_STAGE_LIST.remove(CHALLENGE_NAME_FULL)
non_challenge_stages = duplicate_list(STAGE_NAME_LIST)
if CHALLENGE_NAME_FULL in non_challenge_stages: non_challenge_stages.remove(CHALLENGE_NAME_FULL)

non_story_pool = duplicate_list(STAGE_NAME_LIST)
if CHALLENGE_NAME_FULL in non_story_pool: non_story_pool.remove(CHALLENGE_NAME_FULL)
if TUTORIAL_NAME_FULL in non_story_pool: non_story_pool.remove(TUTORIAL_NAME_FULL)
non_stage6_pool = duplicate_list(non_story_pool)
if STAGE6_NAME_FULL in non_stage6_pool: non_stage6_pool.remove(STAGE6_NAME_FULL)

# conditions
progressive_stages_enabled = OptionFilter(ProgressiveStages, True)
progressive_stages_disabled = OptionFilter(ProgressiveStages, False)
progressive_loadout_together = OptionFilter(ProgressiveLoadout, ProgressiveLoadout.option_together)
progressive_loadout_separate = OptionFilter(ProgressiveLoadout, ProgressiveLoadout.option_separate)
progressive_loadout_disabled = OptionFilter(ProgressiveLoadout, ProgressiveLoadout.option_none)
low_skill_scale = OptionFilter(LowSkillLogic, LowSkillLogic.option_scale)
low_skill_full = OptionFilter(LowSkillLogic, LowSkillLogic.option_full)
low_skill_none = OptionFilter(LowSkillLogic, LowSkillLogic.option_none)
low_skill_stats_on = OptionFilter(LowSkillStats, True)
low_skill_stats_off = OptionFilter(LowSkillStats, False)
treasure_hunt_on = OptionFilter(CompletionType, CompletionType.option_dragon_gems)

def get_card_shop_item_names() -> list[str]:
    # Go through both lists and fetch the card names.
    # Nazrin's cards never show up in shop.
    shop_card_item_names = []
    for card_string_id in ABILITY_CARD_LIST:
        if card_string_id == NAZRIN_CARD_1 or card_string_id == NAZRIN_CARD_2: continue
        shop_card_item_names.append(CARD_ID_TO_NAME[card_string_id])
    return shop_card_item_names


def low_skill_check(stage_id: int = 0):
    """
    Runs a proper check on whether the player has all cards needed to satisfy the low skill logic requirements.
    If low skill logic is disabled entirely, this returns True.
    """
    def get_low_skill_loadout(card_count: int = 1):
        """
        Filters to False by default if Low Skill Logic is not enabled.
        """
        scaled_loadout_rule = HasFromListUnique(*LOW_SKILL_CARD_LIST, count=card_count, options=[low_skill_scale])
        full_loadout_rule = HasAll(*LOW_SKILL_CARD_LIST, options=[low_skill_full])

        return scaled_loadout_rule | full_loadout_rule

    def get_low_skill_stats(is_scaled_stat: bool = False, stat_count: int = 6):
        """
        Filters to True if Low Skill Stats is not enabled.
        Should only be used in conjunction with Low Skill Logic.
        """
        if is_scaled_stat:
            equip_slot_count = clamp(stat_count, 0, 6)
            cost_count = clamp(stat_count, 0, 5)
        else:
            equip_slot_count = 6
            cost_count = 5

        together_stat_rule = Has(PROGRESS_EQUIP_NAME, count=equip_slot_count, options=[low_skill_stats_on, progressive_loadout_together])
        separate_stat_rule = Has(PROGRESS_SLOT_NAME, count=equip_slot_count, options=[low_skill_stats_on, progressive_loadout_separate]) & Has(PROGRESS_COST_NAME, count=cost_count, options=[low_skill_stats_on, progressive_loadout_separate])
        none_of_the_above_rule = (progressive_loadout_disabled & True_()) | (low_skill_stats_off & True_())

        return together_stat_rule | separate_stat_rule | none_of_the_above_rule

    def get_low_skill_none():
        return low_skill_none & True_()

    # Stage 6 and Challenge Market remains unchanged.
    if stage_id == STAGE6_ID or stage_id == STAGE_CHALLENGE_ID:
        return (HasAll(*LOW_SKILL_CARD_LIST) & get_low_skill_stats()) | get_low_skill_none()
    elif stage_id == BOSS_TAKANE:
        TAKANE_CARD_LIST = LOW_SKILL_CARD_LIST + [MIKE_CARD_NAME]
        return (HasAll(*TAKANE_CARD_LIST) & get_low_skill_stats()) | get_low_skill_none()

    has_scaled_low_skill = low_skill_scale & True_()
    has_full_low_skill = low_skill_full & True_()

    # Adds scaling.
    if stage_id == STAGE4_ID:
        has_scaled_low_skill = get_low_skill_loadout(2) & get_low_skill_stats(True, 2)
        has_full_low_skill = get_low_skill_loadout() & get_low_skill_stats()
    elif stage_id == STAGE5_ID:
        has_scaled_low_skill = get_low_skill_loadout(4) & get_low_skill_stats(True, 4)
        has_full_low_skill = get_low_skill_loadout() & get_low_skill_stats()
    elif stage_id == STAGE_CHIMATA_ID:
        has_scaled_low_skill = HasFromListUnique(*END_MARKET_CARD_LIST, count=3, options=[low_skill_scale]) & get_low_skill_stats(True, 5)
        has_full_low_skill = HasAll(*END_MARKET_CARD_LIST, options=[low_skill_full]) & get_low_skill_stats()

    # If none of the above cases apply, pass it as True.
    return has_scaled_low_skill | has_full_low_skill | get_low_skill_none()

def low_skill_check_nitori():
    loadout_together = progressive_loadout_together & low_skill_check(STAGE_CHIMATA_ID) & Has(PROGRESS_EQUIP_NAME, count=1)
    loadout_separate = progressive_loadout_separate & low_skill_check(STAGE_CHIMATA_ID) & Has(PROGRESS_SLOT_NAME, count=1)
    loadout_none = (progressive_loadout_disabled & low_skill_check(STAGE_CHIMATA_ID) &
                    (Has(PROGRESS_STAGE_ITEM_NAME, count=1) | HasFromListUnique(*STANDARD_STAGE_LIST, count=1)))

    return loadout_together | loadout_separate | loadout_none


def low_skill_check_encounters(stage_id: int = 0):
    if stage_id == BOSS_NITORI:
        return Has(JUNKO_CARD_NAME) | low_skill_check_nitori()
    return Has(JUNKO_CARD_NAME) | low_skill_check(stage_id)


def has_equipment_achievement_access():
    loadout_together = progressive_loadout_together & Has(PROGRESS_EQUIP_NAME, count=6)
    loadout_separate = progressive_loadout_separate & Has(PROGRESS_SLOT_NAME, count=6)
    loadout_none = progressive_loadout_disabled & has_stage_access_item_count(4)
    return loadout_together | loadout_separate | loadout_none


# Tutorial stage has 5 exclusive cards.
def has_tutorial_access_item():
    return Has(PROGRESS_STAGE_ITEM_NAME) | Has(TUTORIAL_NAME_FULL)


def has_challenge_access_item(is_boss: bool = False):
    """
    Checks for Challenge Market access. Also checks for Low Skill Logic.
    If generation has turned off Challenge Market in logic (disable_challenge_logic == true),
    this will always return False.
    If doing Progressive Stages, also return False.
    """
    progressive_market = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(CHALLENGE_NAME), options=[progressive_stages_enabled])
    nonprogressive_market = (Has(CHALLENGE_NAME_FULL, options=[OptionFilter(DisableChallengeLogic, False)]) |
                             HasAll(*STAGE_NAME_LIST, options=[OptionFilter(DisableChallengeLogic, True)]))
    nonprog_extra = progressive_stages_disabled & True_()

    is_boss_conditional = True_()
    if not is_boss: is_boss_conditional = False_()

    return (progressive_market | (nonprogressive_market & nonprog_extra & is_boss_conditional)) & low_skill_check(STAGE_CHALLENGE_ID)


# For specific stages (excludes Challenge Market by default).
def has_stage_access_item(short_stage_name: str):
    full_stage_name = STAGE_SHORT_TO_FULL_NAME[short_stage_name]

    progressive_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(short_stage_name), options=[progressive_stages_enabled])
    nonprogressive_access = Has(full_stage_name)

    return (progressive_access | nonprogressive_access) & low_skill_check(STAGE_NAME_TO_ID[short_stage_name])


def has_stage_list_access_item(stage_name_list: list[str], achieve_check: bool = False):
    """
    Checks for whether the player would have any of the stages available.
    When checking for Progressive Market requirements, this will always take the first name on the list.
    Challenge Market-related checks have their own separate condition.

    :param world: Just pass in world from Rules.py
    :param state: CollectionState. Just pass the one from the lambda in.
    :param stage_name_list: The full names of the stages.
    :param achieve_check: Whether this is for Achievements or not.
    """

    progressive_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(stage_name_list[0], True))
    nonprogressive_access = HasAny(*stage_name_list)
    if achieve_check: nonprogressive_access = HasAll(*stage_name_list)

    return progressive_access | nonprogressive_access


def has_any_stage_access_item():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME)
    nonprogress_access = HasAny(*non_challenge_stages) | has_challenge_access_item()

    return progress_access | nonprogress_access


# Despite the name, this is actually used for the slot upgrade achievement.
def has_stage_access_item_count(stage_count: int):
    if stage_count <= 0: return True_()

    def item_count_stages(used_count: int):
        local_progress_access = HasFromListUnique(*non_story_pool, count=used_count, options=[OptionFilter(DisableChallengeLogic, True)])

        nonprogress_used_count = clamp(used_count - 1, 0, len(non_story_pool))
        local_nonprogress_access = (HasFromListUnique(*non_stage6_pool, count=nonprogress_used_count) &
                                    HasFromListUnique(STAGE6_NAME_FULL, CHALLENGE_NAME_FULL, count=1) &
                                    OptionFilter(DisableChallengeLogic, False))

        return local_progress_access | local_nonprogress_access

    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, count=stage_count, options=[progressive_stages_enabled])
    nonprogress_access = (item_count_stages(stage_count) |
                          (HasAll(TUTORIAL_NAME_FULL, STAGE4_NAME_FULL, BLANK_CARD_NAME, STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME, ENDSTAGE_NAME_FULL) &
                           item_count_stages(stage_count - 1))) & progressive_stages_disabled

    return progress_access | nonprogress_access


# For more open reward pools. Of course, these all imply Challenge Market clauses as well.
# Common. Shows up in every stage except Tutorial.
def has_common_access_item():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE1_NAME),
                          options=[progressive_stages_enabled])
    nonprogress_access = (HasAny(*non_story_pool) | has_challenge_access_item()) & progressive_stages_disabled

    return progress_access | nonprogress_access


# Very early game (Stage 1+). Does not show up in Stage 5 or End of Market.
def has_very_early_game_access_item():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, get_progress_item_requirement(STAGE1_NAME), options=[progressive_stages_enabled])
    nonprogress_access = (has_early_game_access_item() | Has(STAGE1_NAME_FULL)) & progressive_stages_disabled
    return progress_access | nonprogress_access


# Early game (Stage 2+). Does not show up in Stage 5 or End of Market.
def has_early_game_access_item():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, get_progress_item_requirement(STAGE2_NAME), options=[progressive_stages_enabled])
    nonprogress_access = (has_midgame_access_item() | Has(STAGE2_NAME_FULL)) & progressive_stages_disabled
    return progress_access | nonprogress_access


# Midgame (Stage 3+). Does not show up in Stage 5 or End of Market.
def has_midgame_access_item():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, get_progress_item_requirement(STAGE3_NAME), options=[progressive_stages_enabled])
    nonprogress_access = ((has_challenge_access_item() |
                        (Has(STAGE3_NAME_FULL) |
                        (Has(STAGE4_NAME_FULL) & low_skill_check(STAGE4_ID)) |
                        (Has(STAGE6_NAME_FULL) & low_skill_check(STAGE6_ID)))) &
                        progressive_stages_disabled)
    return progress_access | nonprogress_access


# Lategame (Stage 4+). Does not show up in End of Market.
# Low Skill Logic forces the generation to include certain Ability Cards as compulsory.
def has_lategame_access_item():
    progress_access = (Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE4_NAME), options=[progressive_stages_enabled]) &
                       low_skill_check(STAGE6_ID))
    nonprogress_access = ((Has(STAGE4_NAME_FULL) & low_skill_check(STAGE4_ID)) |
                          (Has(STAGE5_NAME_FULL) & low_skill_check(STAGE5_ID)) |
                          (Has(STAGE6_NAME_FULL) & low_skill_check(STAGE6_ID)) |
                          (has_challenge_access_item() & low_skill_check(STAGE_CHALLENGE_ID))) & progressive_stages_disabled
    return progress_access | nonprogress_access


def has_encounter_access(condition):
    # Special checks.
    if condition == BOSS_NITORI:
        # Checks if the player has Stage access and the right cards for access.
        return has_nitori_boss_access() & low_skill_check_encounters(BOSS_NITORI)
    elif condition == BOSS_TAKANE:
        return has_takane_boss_access() & low_skill_check_encounters(BOSS_TAKANE)
    elif condition == CHALLENGE_NAME:
        return has_challenge_access_item(True)
    # None of the special cases apply.
    return has_stage_access_item(condition) & low_skill_check_encounters(STAGE_NAME_TO_ID[condition])


def has_nitori_boss_access():
    progress_access = (Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE4_NAME), options=[progressive_stages_enabled]) &
                       Has(BLANK_CARD_NAME))
    nonprogress_access = HasAll(STAGE4_NAME_FULL, BLANK_CARD_NAME, options=[progressive_stages_disabled])
    return progress_access | nonprogress_access


# Special access rules.
def has_nitori_access():
    return has_nitori_boss_access() & low_skill_check_nitori()


def has_takane_boss_access():
    progress_access = (Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE6_NAME), options=[progressive_stages_enabled]) &
                       Has(NITORI_STORY_CARD_NAME))
    nonprogress_access = HasAll(STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME, options=[progressive_stages_disabled])
    return progress_access | nonprogress_access


def has_takane_access():
    return has_takane_boss_access() & low_skill_check(STAGE6_ID)


def has_sekibanki_access():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE2_NAME), options=[progressive_stages_enabled])
    nonprogress_access = HasAny(STAGE2_NAME_FULL, ENDSTAGE_NAME_FULL) | has_challenge_access_item()
    return progress_access | nonprogress_access


# Lily White's and Doremy's cards are a little more open.
def has_lily_white_access():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE1_NAME), options=[progressive_stages_enabled])
    nonprogress_access = (has_very_early_game_access_item() | has_challenge_access_item() |
                          (has_stage_access_item(STAGE5_NAME) & low_skill_check(STAGE5_ID)))
    return progress_access | nonprogress_access


def has_doremy_access():
    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE2_NAME), options=[progressive_stages_enabled])
    nonprogress_access = (has_early_game_access_item() | has_challenge_access_item() |
                          (has_stage_access_item(STAGE5_NAME) & low_skill_check(STAGE5_ID)))
    return progress_access | nonprogress_access


def has_nazrin2_access():
    black_market_stages = duplicate_list(STAGE_NAME_LIST)
    if ENDSTAGE_NAME_FULL in black_market_stages:
        black_market_stages.remove(ENDSTAGE_NAME_FULL)
    if CHALLENGE_NAME_FULL in black_market_stages:
        black_market_stages.remove(CHALLENGE_NAME_FULL)

    progress_access = Has(PROGRESS_STAGE_ITEM_NAME, options=[progressive_stages_enabled])
    nonprogress_access = HasAny(*black_market_stages) | has_challenge_access_item()
    return progress_access | nonprogress_access


def all_bosses_access():
    """
    Checks if the player can access all bosses outside of Challenge Market.
    This accounts for not only all stage unlocks but also the two special cards.
    """
    progress_access = (
        progressive_stages_enabled &
        Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(ENDSTAGE_NAME)) &
        HasAll(BLANK_CARD_NAME, NITORI_STORY_CARD_NAME) &
        low_skill_check(BOSS_TAKANE)
    )
    nonprogress_access = (
        HasAll(*non_challenge_stages) &
        HasAll(NITORI_STORY_CARD_NAME, BLANK_CARD_NAME) &
        low_skill_check(STAGE6_ID) & low_skill_check(STAGE_CHIMATA_ID)
    )
    return progress_access | nonprogress_access


def all_cards_access():
    return HasAll(*get_card_shop_item_names())


# Access rules for the Ability Card dex entries.
# Ensures that the player has a way to grind for Funds + the card in the Permanent Card Shop.
# This will fail if this is a solo game and the player chooses to start with no Markets unlocked.
# (Hopefully)
def has_grind_access(the_card_id: str):
    return Has(CARD_ID_TO_NAME[the_card_id]) & has_any_stage_access_item()


def add_generic_access_card_rule(world, card_name_id: str, access_level: int):
    generic_location_card_name: str = get_card_location_name_str(card_name_id, False)
    generic_location_card = world.get_location(generic_location_card_name)

    match access_level:
        case 0:  # Common access.
            world.set_rule(generic_location_card, has_common_access_item())
        case 1:  # Stage 1+
            world.set_rule(generic_location_card, has_very_early_game_access_item())
        case 2:  # Stage 2+
            world.set_rule(generic_location_card, has_early_game_access_item())
        case 3:  # Stage 3+
            world.set_rule(generic_location_card, has_midgame_access_item())
        case 4:  # Lategame
            world.set_rule(generic_location_card, has_lategame_access_item())
        case _:
            pass

def get_goal_condition(world):
    def minimum_story_clear():
        progress_access = (Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(STAGE6_NAME)) &
                           Has(NITORI_STORY_CARD_NAME) & progressive_stages_enabled)
        nonprogress_access = (HasAll(NITORI_STORY_CARD_NAME, STAGE6_NAME_FULL) & progressive_stages_disabled)
        return (progress_access | nonprogress_access) & low_skill_check(BOSS_TAKANE)

    def full_story_clear():
        progress_access = (
            Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(ENDSTAGE_NAME)) &
            HasAll(NITORI_STORY_CARD_NAME, BLANK_CARD_NAME)
        )
        nonprogress_access = HasAll(NITORI_STORY_CARD_NAME, BLANK_CARD_NAME, STAGE4_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL)

        return (progress_access | nonprogress_access) & low_skill_check(BOSS_TAKANE) & low_skill_check_nitori()

    # To defeat all bosses, you need all stages to be available except the Challenge Market.
    # Both instances of Mike Goutokuji are counted.
    boss_condition_list = duplicate_list(STAGE_NAME_LIST)
    if CHALLENGE_NAME_FULL in boss_condition_list: boss_condition_list.remove(CHALLENGE_NAME_FULL)

    def all_bosses_clear():
        # If Progressive Stages is enabled, this is just straight up Full Story Clear conditions.
        progress_access = full_story_clear() & progressive_stages_enabled
        nonprogress_access = (
            HasAll(NITORI_STORY_CARD_NAME, BLANK_CARD_NAME, *boss_condition_list) &
            progressive_stages_disabled
        )
        return (progress_access | nonprogress_access) & low_skill_check_nitori() & low_skill_check(BOSS_TAKANE)

    def full_clear_rule():
        progress_access = (HasAll(*get_card_shop_item_names(), options=[progressive_stages_enabled]) &
                           full_story_clear())
        nonprogress_access = (
            HasAll(*get_card_shop_item_names(), *boss_condition_list, options=[progressive_stages_disabled])
        )
        return progress_access | nonprogress_access

    def dragon_gem_hunt():
        # This will only ever be called if the completion type is Dragon Gem Hunt anyways.
        # No need to add an option filter here.
        return Has(DRAGON_GEM_ITEM_NAME, count=world.options.dragon_gems_condition.value)

    completion_type: int = world.options.completion_type

    if completion_type == CompletionType.option_full:
        return full_story_clear()
    elif completion_type == CompletionType.option_min:
        return minimum_story_clear()
    elif completion_type == CompletionType.option_cards:
        return all_cards_access()
    elif completion_type == CompletionType.option_bosses:
        return all_bosses_clear()
    elif completion_type == CompletionType.option_challenge:
        return has_challenge_access_item(True)
    elif completion_type == CompletionType.option_true_all:
        return full_clear_rule() & has_challenge_access_item(True)
    elif completion_type == CompletionType.option_dragon_gems:
        return dragon_gem_hunt()
    else:
        return full_clear_rule()