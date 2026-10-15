"""Compila o módulo C++ NexusRoyale (GAS: AS_Hero, UNRAbilitySystemComponent, inventário, HUD).

Uso (com a Unreal FECHADA):   python -I Unreal/ue_gas_compilar.py [--abrir]
  1. confere se há Visual Studio com o MSVC (UE 5.8: 14.44.35211+ do VS 2022 17.14 ou 14.50.35723+ do VS 2026);
  2. recusa rodar com o editor aberto (o módulo novo só carrega numa abertura nova);
  3. põe o módulo "NexusRoyale" e o plugin GameplayAbilities no NexusRoyale.uproject (só se faltarem);
  4. roda o Build.bat do editor (NexusRoyaleEditor Win64 Development);
  5. com --abrir, abre o editor com -culture=en (IDs da DSL em inglês; ver AGENTS.md §5).
O código-fonte fica em Unreal/NexusRoyale/Source/NexusRoyale.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UPROJECT = os.path.join(HERE, "NexusRoyale", "NexusRoyale.uproject")
UE = r"D:\Epic Games\UE_5.8"
BUILD = os.path.join(UE, r"Engine\Build\BatchFiles\Build.bat")
EDITOR = os.path.join(UE, r"Engine\Binaries\Win64\UnrealEditor.exe")
VSWHERE = os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                       r"Microsoft Visual Studio\Installer\vswhere.exe")


def falhar(msg):
    print("ERRO:", msg)
    sys.exit(1)


def visual_studio():
    if not os.path.exists(VSWHERE):
        return None
    out = subprocess.run([VSWHERE, "-latest", "-products", "*", "-requires",
                          "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
                         capture_output=True, text=True).stdout.strip()
    return out or None


def editor_aberto():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe"], capture_output=True, text=True).stdout
    return "UnrealEditor.exe" in out


def ajustar_uproject():
    with open(UPROJECT, encoding="utf-8-sig") as f:
        proj = json.load(f)
    mudou = False
    modulos = proj.setdefault("Modules", [])
    if not any(m.get("Name") == "NexusRoyale" for m in modulos):
        modulos.append({"Name": "NexusRoyale", "Type": "Runtime", "LoadingPhase": "Default",
                        "AdditionalDependencies": ["Engine", "GameplayAbilities"]})
        mudou = True
    plugins = proj.setdefault("Plugins", [])
    if not any(p.get("Name") == "GameplayAbilities" for p in plugins):
        plugins.append({"Name": "GameplayAbilities", "Enabled": True})
        mudou = True
    if mudou:
        with open(UPROJECT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(proj, f, indent="\t", ensure_ascii=False)
            f.write("\n")
    print("uproject:", "atualizado" if mudou else "já estava pronto")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    vs = visual_studio()
    if not vs:
        falhar("Visual Studio com C++ não encontrado. Veja AGENTS.md, seção 3, 'Pendências do usuário'.")
    print("Visual Studio:", vs)
    msvc = os.path.join(vs, r"VC\Tools\MSVC")
    if os.path.isdir(msvc):
        print("MSVC:", ", ".join(sorted(os.listdir(msvc))))
    if editor_aberto():
        falhar("a Unreal está aberta. Salve tudo, feche o editor e rode de novo.")
    ajustar_uproject()
    cmd = [BUILD, "NexusRoyaleEditor", "Win64", "Development", f"-Project={UPROJECT}", "-WaitMutex", "-NoHotReloadFromIDE"]
    print("compilando:", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    linhas = (r.stdout + r.stderr).splitlines()
    erros = [l for l in linhas if " error " in l or "error C" in l or "error LNK" in l or ": error" in l]
    print("\n".join(erros[:40] if erros else linhas[-25:]))
    if r.returncode != 0:
        falhar(f"a compilação falhou (código {r.returncode}). Log completo: %LOCALAPPDATA%\\UnrealBuildTool\\Log.txt")
    print("compilou.")
    if "--abrir" in sys.argv:
        subprocess.Popen([EDITOR, UPROJECT, "-culture=en"])
        print("editor abrindo com -culture=en")


if __name__ == "__main__":
    main()
