"""Helpers to import Quaternius glTF/GLB packs through Interchange, optionally forcing a shared skeleton."""
import unreal

eal = unreal.EditorAssetLibrary
QROOT = r"D:\meus documentos\Fortnite\Quaternius"
DEFAULT_ASSETS_PIPELINE = "/Interchange/Pipelines/DefaultAssetsPipeline"


def make_pipeline(skeleton=None, only_animations=False, ignore_vertex_colors=False):
    """Project copy of the default Interchange assets pipeline with optional overrides."""
    name = "P_Assets_" + (skeleton.get_name() if skeleton else "Default") + ("_AnimOnly" if only_animations else "") \
        + ("_NoVColor" if ignore_vertex_colors else "")
    path = f"/Game/Quaternius/Pipelines/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    pipe = eal.duplicate_asset(DEFAULT_ASSETS_PIPELINE, path)
    common = pipe.get_editor_property("common_skeletal_meshes_and_animations_properties")
    if skeleton is not None:
        common.set_editor_property("skeleton", skeleton)
    if only_animations:
        common.set_editor_property("import_only_animations", True)
    if ignore_vertex_colors:
        # Quaternius city meshes store wear masks in vertex colors; the glTF material multiplies them -> red tint
        meshes = pipe.get_editor_property("common_meshes_properties")
        enum = unreal.InterchangeVertexColorImportOption
        ignore = next(getattr(enum, n) for n in dir(enum) if n.endswith("IGNORE"))
        meshes.set_editor_property("vertex_color_import_option", ignore)
    eal.save_loaded_asset(pipe)
    return pipe


def import_interchange(file_path, dest, skeleton=None, only_animations=False, ignore_vertex_colors=False):
    mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
    src = unreal.InterchangeManager.create_source_data(file_path)
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    if skeleton is not None or only_animations or ignore_vertex_colors:
        pipe = make_pipeline(skeleton, only_animations, ignore_vertex_colors)
        try:
            params.override_pipelines = [unreal.SoftObjectPath(pipe.get_path_name())]
        except Exception:
            params.override_pipelines = [pipe]
    res = mgr.import_asset(dest, src, params)
    return [o.get_path_name() for o in (res or [])]


def assets_in(folder, cls_name=None):
    out = []
    for p in eal.list_assets(folder, recursive=True):
        c = str(eal.find_asset_data(p).asset_class_path.asset_name)
        if cls_name is None or c == cls_name:
            out.append(p.split(".")[0])
    return out
