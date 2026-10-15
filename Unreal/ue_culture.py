"""Switch the editor culture for this session only (not saved): ue_py.py ue_culture.py  -> toggles via env below."""
import os

import unreal

target = os.environ.get("UE_CULTURE", "en")
lib = unreal.InternationalizationLibrary
print("current:", lib.get_current_culture(), "->", target)
lib.set_current_culture(target, False)
print("now:", lib.get_current_culture())
