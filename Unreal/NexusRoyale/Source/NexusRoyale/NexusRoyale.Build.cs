using UnrealBuildTool;

// Módulo C++ do Nexus Royale: só o que o Blueprint não consegue fazer sozinho
// (AttributeSet do GAS, efeitos com SetByCaller, inventário e a tabela de itens). O resto é Blueprint.
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
