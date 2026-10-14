import unittest

from .. import DISPLAY_NAME, TouhouHBMWorld, STAGE_CHALLENGE_ID
from ..Tools import get_boss_names_challenge_list, get_boss_location_name_str, get_stage_clear_location_name_str


class PythonTestFunctions(unittest.TestCase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    def test_slice(self):
        list = ["REIMU", "MARISA", "SAKUYA", "SANAE"]
        print(list[1:-1])
        # list[1:] prints ["MARISA", "SAKUYA", "SANAE"]
        # list[:-1] prints ["REIMU", "MARISA", "SAKUYA"]
        #
        # list[-2:] prints ["SAKUYA", "SANAE"]
        # list[list.index("MARISA"):] includes ["MARISA"] + the above.
        # list[-list.index("MARISA"):] removes ["SAKUYA"] from the above.
        # list[-list.index("MARISA"):] removes ["SAKUYA"] from the above.

    def test_challenge_names(self):
        print(get_stage_clear_location_name_str(STAGE_CHALLENGE_ID))