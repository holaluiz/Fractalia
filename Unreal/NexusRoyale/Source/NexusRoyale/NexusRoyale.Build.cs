using UnrealBuildTool;

// Módulo C++ do Nexus Royale: o núcleo replicado (estado da partida, GAS, inventário, combate) e o que o Blueprint
// não consegue fazer sozinho. Conteúdo, visual e números ficam em Blueprint e dados (Docs/Game/TECHNICAL_ARCHITECTURE.md).
public class NexusRoyale : ModuleRules
{
	public NexusRoyale(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"GameplayAbilities",
			"GameplayTags",
			"GameplayTasks",
			"UMG",
			"Slate",
			"SlateCore"
		});

		PublicIncludePaths.Add(ModuleDirectory);
	}
}
