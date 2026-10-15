import unreal

print("engine:", unreal.SystemLibrary.get_engine_version())
print("project:", unreal.Paths.get_project_file_path())
print("level:", unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level())
print("IKRigController:", hasattr(unreal, "IKRigController"), "| IKRetargeterController:", hasattr(unreal, "IKRetargeterController"))
