# Creates the NexusRoyale Unreal project from the engine's Third Person (Blueprint) template,
# the same way the editor's New Project wizard does (template content + shared packs + renames),
# and enables the MCP / toolsets / Python plugins with the MCP server auto-starting.
param(
    [string]$Engine = "D:\Epic Games\UE_5.8",
    [string]$Project = "D:\meus documentos\Fortnite\Unreal\NexusRoyale",
    [string]$Name = "NexusRoyale"
)
$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding $false
$tpl = Join-Path $Engine "Templates\TP_ThirdPersonBP"
$packs = Join-Path $Engine "Templates\TemplateResources\High"

if (Test-Path (Join-Path $Project "$Name.uproject")) { Write-Output "Project already exists: $Project"; exit 0 }
New-Item -ItemType Directory -Force $Project, "$Project\Config", "$Project\Content" | Out-Null

function Copy-Tree($from, $to) {
    robocopy $from $to /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE): $from -> $to" }
}

# template content + config (minus template-only files)
Copy-Tree "$tpl\Content" "$Project\Content"
Get-ChildItem "$tpl\Config" -File | Where-Object { $_.Name -notin @("TemplateDefs.ini", "config.ini") } |
    Copy-Item -Destination "$Project\Config"
# shared content packs referenced by TemplateDefs.ini
foreach ($p in "Characters", "Input", "LevelPrototyping") { Copy-Tree "$packs\$p\Content" "$Project\Content\$p" }

# template name -> project name in config files
Get-ChildItem "$Project\Config" -Filter *.ini | ForEach-Object {
    $t = [IO.File]::ReadAllText($_.FullName) -replace "TP_ThirdPersonBP", $Name
    [IO.File]::WriteAllText($_.FullName, $t, $utf8)
}
$g = [guid]::NewGuid().ToByteArray()
$ids = 0..3 | ForEach-Object { [BitConverter]::ToInt32($g, $_ * 4) }
$game = [IO.File]::ReadAllText("$Project\Config\DefaultGame.ini")
$game = $game -replace "ProjectID=\(.*?\)", "ProjectID=(A=$($ids[0]),B=$($ids[1]),C=$($ids[2]),D=$($ids[3]))"
$game = $game -replace "ProjectName=.*", "ProjectName=Nexus Royale"
[IO.File]::WriteAllText("$Project\Config\DefaultGame.ini", $game, $utf8)

$uproject = @"
{
	"FileVersion": 3,
	"EngineAssociation": "5.8",
	"Category": "",
	"Description": "Nexus Royale - battle royale com herois de MOBA",
	"Plugins": [
		{ "Name": "ModelingToolsEditorMode", "Enabled": true, "TargetAllowList": [ "Editor" ] },
		{ "Name": "GameplayStateTree", "Enabled": true },
		{ "Name": "ModelContextProtocol", "Enabled": true },
		{ "Name": "AllToolsets", "Enabled": true },
		{ "Name": "PythonScriptPlugin", "Enabled": true }
	]
}
"@
[IO.File]::WriteAllText("$Project\$Name.uproject", $uproject, $utf8)

# per-user editor settings: start the MCP server with the editor
$userCfg = "$Project\Saved\Config\WindowsEditor"
New-Item -ItemType Directory -Force $userCfg | Out-Null
$ini = @"
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
"@
[IO.File]::WriteAllText("$userCfg\EditorPerProjectUserSettings.ini", $ini, $utf8)

Write-Output "Created $Project\$Name.uproject"
