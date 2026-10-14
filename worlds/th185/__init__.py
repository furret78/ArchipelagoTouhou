from .Tools import get_progress_item_count
from .WebWorld import TouhouHBMWebWorld
from .variables.boss_and_stage import *
from ..LauncherComponents import Component, components, launch_subprocess, Type, icon_paths
from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World
from . import Locations, Items, Options as HBMOptions, Regions, Rules
from .variables.meta_data import *

def launch_client():
    """
    Launch a Client instance.
    """
    from .Client import launch
    launch_subprocess(launch, name="GameClient")

components.append(Component(
    display_name=SHORT_NAME+" Client",
    func=launch_client,
    component_type=Type.CLIENT,
    game_name=DISPLAY_NAME,
    icon="th185_card",
    description="AP Client for Black Market of Bulletphilia ~ 100th Black Market."
))

icon_paths["th185_card"] = f"ap:{__name__}/icons/th185_card.png"

class TouhouHBMWorld(World):
    """
    The marketplace god spoke.
    "The Ability Cards will inevitably spread, inevitably become obsolete,
    and the market will return to its everyday routine."
    But contrary to the god's intent, the value of the cards is somehow rising further and further.
    Could someone be manipulating their value?
    Or could it be because a select few collectors are buying up all the stock?
    When the card market had reached the utter peak of chaos,
    markets that the god couldn't intervene in--"black markets"--began to open.
    (from thpatch.net)
    """
    game = DISPLAY_NAME
    web = TouhouHBMWebWorld()

    location_name_to_id = Locations.location_table
    item_name_to_id = Items.get_item_to_id_dict()

    options_dataclass = HBMOptions.TouhouHBMDataclass
    options: HBMOptions.TouhouHBMDataclass

    origin_region_name = "Menu"

    item_name_groups = Items.get_item_groups()
    location_name_groups = Locations.location_groups

    def generate_early(self) -> None:
        # Check if the input looks too ridiculous.
        # Starting at Challenge Market without Progressive Market but has Disable Challenge Market on.
        # As well as lacking any other free checks.
        if not self.options.progressive_stages and self.options.starting_market.value == 8 and not self.options.music_room_checks:
            if self.options.disable_challenge_logic:
                raise Exception(f"You chose to start on Challenge Market without Progressive Market enabled and without disabling early Challenge Market. {GEN_UNWINNABLE}")
            if self.options.low_skill_logic.value != 0:
                raise Exception(f"You chose to start on Challenge Market without any Ability Cards that generation rules require. {GEN_UNWINNABLE}")

        # Set early game placements priority here.
        if self.options.anti_grinding_toggle and self.options.anti_grinding_placements.value:
            for card_item_name in self.options.anti_grinding_placements.value:
                self.multiworld.local_early_items[self.player][card_item_name] = 1

        # Push Starting Market items.
        if self.options.progressive_stages:
            progress_items_to_push: int = get_progress_item_count(self.options.starting_market.value)

            progress_items_given = 0
            while progress_items_given < progress_items_to_push:
                self.push_precollected(self.create_item(PROGRESS_STAGE_ITEM_NAME))
                progress_items_given += 1

            return

        item_name_to_push: str = TUTORIAL_NAME_FULL

        match self.options.starting_market.value:
            case 1: item_name_to_push = STAGE1_NAME_FULL
            case 2: item_name_to_push = STAGE2_NAME_FULL
            case 3: item_name_to_push = STAGE3_NAME_FULL
            case 4: item_name_to_push = STAGE4_NAME_FULL
            case 5: item_name_to_push = STAGE5_NAME_FULL
            case 6: item_name_to_push = STAGE6_NAME_FULL
            case 7: item_name_to_push = ENDSTAGE_NAME_FULL
            case 8: item_name_to_push = CHALLENGE_NAME_FULL
            case _: item_name_to_push = TUTORIAL_NAME_FULL

        self.push_precollected(self.create_item(item_name_to_push))

    def create_regions(self):
        Regions.create_and_connect_regions(self)
        Locations.create_all_locations(self)

    def set_rules(self) -> None:
        Rules.set_all_rules(self)

    def create_items(self) -> None:
        Items.create_all_items(self)

    def create_item(self, name: str) -> Items.TouhouHBMItem:
        return Items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return Items.get_random_filler_item_name(self)

    # The place where player data goes.
    def fill_slot_data(self) -> Mapping[str, Any]:
        data = {
            # Options
            "starting_market": self.options.starting_market.value,
            "progressive_stages": self.options.progressive_stages.value,
            "progressive_loadout": self.options.progressive_loadout.value,
            "progressive_loadout_count": self.options.progressive_loadout_count.value,
            "progressive_cost_count": self.options.progressive_cost_count.value,
            "progressive_slot_count": self.options.progressive_slot_count.value,
            "stage_boss_locations": self.options.stage_boss_locations.value,
            "disable_challenge_logic": self.options.disable_challenge_logic.value,
            "trap_chance": self.options.trap_chance.value,
            "trap_blacklist": self.options.trap_blacklist.value,
            "trap_durations": self.options.trap_durations.value,
            "low_skill_logic": self.options.low_skill_logic.value,
            "low_skill_stats": self.options.low_skill_stats.value,
            "include_gameplay_filler": self.options.include_gameplay_filler.value,
            "dragon_gems_condition": self.options.dragon_gems_condition.value,
            "dragon_gems_pool": self.options.dragon_gems_pool.value,
            "death_link": self.options.death_link.value,
            "death_link_trigger": self.options.death_link_trigger.value,
            "death_link_invincibility": self.options.death_link_invincibility.value,
            "energy_link": self.options.energy_link.value,
            "energy_link_bullet_money": self.options.energy_link_bullet_money.value,
            "music_room_checks": self.options.music_room_checks.value,
            "achievement_checks": self.options.achievement_checks.value,
            "anti_grinding_placements": self.options.anti_grinding_placements.value,
            "anti_grinding_toggle": self.options.anti_grinding_toggle.value,
            "perma_upgrade_toggle": self.options.perma_upgrade_toggle.value,
            "perma_upgrade_life": self.options.perma_upgrade_life.value,
            "perma_upgrade_bm": self.options.perma_upgrade_bm.value,
            "perma_upgrade_power": self.options.perma_upgrade_power.value,
            "perma_upgrade_atk": self.options.perma_upgrade_atk.value,
            "perma_upgrade_magic_atk": self.options.perma_upgrade_magic_atk.value,
            "completion_type": self.options.completion_type.value
        }
        return data