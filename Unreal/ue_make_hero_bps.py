"""Create BP_Hero_<Name> for every hero from the already retargeted ABP_Unarmed_<Name> (no re-retarget)."""
import importlib.util

spec = importlib.util.spec_from_file_location("ue_setup_heroes", r"D:\meus documentos\Fortnite\Unreal\ue_setup_heroes.py")
sh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sh)
sh.main(rebuild_rigs=False)
