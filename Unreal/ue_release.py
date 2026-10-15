"""Empacota o Nexus Royale para Windows e publica a versão no GitHub Releases, de onde o launcher baixa.

Uso (na raiz do projeto):
  python -I Unreal/ue_release.py versao 0.2.0   grava a versão no Config/DefaultGame.ini (ProjectVersion)
  python -I Unreal/ue_release.py compilar       compila o alvo de jogo (NexusRoyale Win64); pode com o editor aberto
  python -I Unreal/ue_release.py empacotar      cook + stage + pak + archive (RunUAT BuildCookRun), com o editor FECHADO
  python -I Unreal/ue_release.py launcher       compila o instalador/launcher em Launcher/bin (csc do Windows)
  python -I Unreal/ue_release.py zipar          zip do jogo + instalador + manifest.json, em D:\\NexusRoyale_Builds\\<versão>
  python -I Unreal/ue_release.py publicar [--notas arq.md]   cria a Release v<versão> em holaluiz/MOBA-BR (gh)
  python -I Unreal/ue_release.py tudo [--versao X.Y.Z] [--notas arq.md]
        empacotar + zipar + publicar. Sem --versao, sobe o último número sozinho se a versão atual já foi publicada.
Opções: --config Development|Shipping (padrão Development: mostra os PrintString e tem console, tecla ').
        --com-editor deixa empacotar com o editor aberto (precisa de muita RAM; evite).
        --sem-cook reaproveita o build e o cook anteriores (só stage, pak e cópia).
O processo completo está no AGENTS.md, seção 5, "Release". O launcher (C#) fica em Launcher/.
Quem joga instala pelo NexusRoyale-Instalador.exe da Release; o atalho "Nexus Royale" confere a última Release
antes de abrir o jogo e baixa a versão nova, se houver.
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
UPROJECT = os.path.join(HERE, "NexusRoyale", "NexusRoyale.uproject")
GAME_INI = os.path.join(HERE, "NexusRoyale", "Config", "DefaultGame.ini")
UE = r"D:\Epic Games\UE_5.8"
BUILD = os.path.join(UE, r"Engine\Build\BatchFiles\Build.bat")
RUNUAT = os.path.join(UE, r"Engine\Build\BatchFiles\RunUAT.bat")
BUILDS = r"D:\NexusRoyale_Builds"
MAPA = "/Game/NexusRoyale/Maps/L_Island"
REPO = "holaluiz/MOBA-BR"
LAUNCHER = os.path.join(RAIZ, "Launcher")
LAUNCHER_CS = os.path.join(LAUNCHER, "NexusRoyaleLauncher.cs")
INSTALADOR = "NexusRoyale-Instalador.exe"
CSC = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
ICONE = os.path.join(UE, r"Engine\Build\Windows\Resources\Default.ico")
PARTE = 1900 * 1024 * 1024          # o GitHub aceita até 2 GiB por arquivo de Release
SEM_COMPRESSAO = (".pak", ".ucas", ".utoc")  # já vêm comprimidos (Oodle) do cook


def falhar(msg):
    print("ERRO:", msg)
    sys.exit(1)


def opcao(nome, padrao=None):
    if nome in sys.argv:
        i = sys.argv.index(nome)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return padrao


def editor_aberto():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe"], capture_output=True, text=True).stdout
    return "UnrealEditor.exe" in out


# --- versão -------------------------------------------------------------------------------------

def ler_ini():
    with open(GAME_INI, "rb") as f:
        bruto = f.read()
    bom = bruto.startswith(b"\xef\xbb\xbf")
    texto = bruto.decode("utf-8-sig")
    return texto, bom, ("\r\n" if "\r\n" in texto else "\n")


def versao_atual():
    texto, _, _ = ler_ini()
    m = re.search(r"^ProjectVersion=(\S+)", texto, re.M)
    return m.group(1) if m else "0.0.0"


def gravar_versao(v):
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        falhar(f"versão '{v}' inválida. Use 3 números, como 0.2.0.")
    texto, bom, nl = ler_ini()
    if re.search(r"^ProjectVersion=", texto, re.M):
        texto = re.sub(r"^ProjectVersion=.*$", f"ProjectVersion={v}", texto, flags=re.M)
    else:
        secao = "[/Script/EngineSettings.GeneralProjectSettings]"
        if secao not in texto:
            texto = texto.rstrip() + nl + nl + secao + nl
        texto = texto.replace(secao, secao + nl + f"ProjectVersion={v}", 1)
    with open(GAME_INI, "wb") as f:
        f.write((b"\xef\xbb\xbf" if bom else b"") + texto.encode("utf-8"))
    print("versão:", v)


# --- build --------------------------------------------------------------------------------------

def rodar(cmd, log):
    """Roda o comando, grava tudo no log e mostra só as linhas que importam."""
    print("rodando:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    print("log:", log)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    marcas = ("**********", "BUILD SUCCESSFUL", "BUILD FAILED", "AutomationTool exiting", "Error:", "error C",
              "error LNK", "Cooked packages", "Packages Cooked", "Took ", "Result:", "Total execution")
    with open(log, "w", encoding="utf-8", errors="replace", buffering=1) as f:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace")
        for linha in p.stdout:
            f.write(linha)
            if any(m in linha for m in marcas):
                print(linha.rstrip()[:240], flush=True)
        return p.wait()


def compilar(cfg):
    log = os.path.join(BUILDS, versao_atual(), f"compilar_{cfg}.log")
    r = rodar([BUILD, "NexusRoyale", "Win64", cfg, f"-Project={UPROJECT}", "-WaitMutex", "-NoHotReloadFromIDE",
               "-NoUBA"], log)
    if r != 0:
        falhar(f"a compilação falhou (código {r}). Veja {log}")
    print("compilou.")


def empacotar(cfg):
    if editor_aberto() and "--com-editor" not in sys.argv:
        falhar("a Unreal está aberta. O cook precisa da RAM toda: combine com as outras sessões, feche o editor e "
               "rode de novo (ou use --com-editor por sua conta).")
    v = versao_atual()
    destino = os.path.join(BUILDS, v)
    jogo = os.path.join(destino, "Windows")
    if os.path.isdir(jogo):
        shutil.rmtree(jogo)
    cmd = [RUNUAT, "BuildCookRun", f"-project={UPROJECT}", "-noP4", "-platform=Win64",
           f"-clientconfig={cfg}", "-build", "-cook", f"-map={MAPA}", "-stage", "-pak", "-iostore",
           "-compressed", "-prereqs", "-nodebuginfo", "-archive", f"-archivedirectory={destino}",
           "-nocompileeditor", "-unattended", "-utf8output",
           # Sem o Unreal Build Accelerator: com a memória virtual quase cheia ele morre com o erro 1455
           # (VirtualAlloc) logo no começo da compilação.
           "-ubtargs=-NoUBA"]
    if "--sem-cook" in sys.argv:   # reaproveita o build e o cook da última vez (só stage, pak e cópia)
        cmd = [{"-build": "-skipbuild", "-cook": "-skipcook"}.get(c, c) for c in cmd]
    r = rodar(cmd, os.path.join(destino, f"BuildCookRun_{cfg}.log"))
    exe = os.path.join(jogo, "NexusRoyale.exe")
    if r != 0 or not os.path.exists(exe):
        falhar(f"o empacotamento falhou (código {r}). Veja o log em {destino}")
    with open(os.path.join(jogo, "versao.txt"), "w", encoding="utf-8") as f:
        f.write(v + "\n")
    print(f"jogo empacotado em {jogo} ({tamanho_pasta(jogo) / 2**20:.0f} MB)")


def tamanho_pasta(p):
    return sum(os.path.getsize(os.path.join(d, a)) for d, _, arqs in os.walk(p) for a in arqs)


# --- launcher -----------------------------------------------------------------------------------

def versao_launcher():
    with open(LAUNCHER_CS, encoding="utf-8") as f:
        m = re.search(r'public const string Versao = "([^"]+)"', f.read())
    return m.group(1) if m else "0.0.0"


def compilar_launcher(saida):
    """Compila o instalador/launcher com o csc do .NET Framework 4, que vem no Windows (C# 5)."""
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    refs = ["System.Windows.Forms.dll", "System.Drawing.dll", "System.IO.Compression.dll",
            "System.IO.Compression.FileSystem.dll", "System.Web.Extensions.dll", "System.Security.dll"]
    cmd = [CSC, "/nologo", "/target:winexe", "/platform:anycpu", "/optimize+", "/codepage:65001",
           f"/win32icon:{ICONE}", f"/out:{saida}"] + [f"/r:{r}" for r in refs] + [LAUNCHER_CS]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not os.path.exists(saida):
        print(r.stdout, r.stderr)
        falhar("o launcher não compilou.")
    print(f"launcher {versao_launcher()} compilado: {saida}")
    return saida


# --- zip e manifest -----------------------------------------------------------------------------

def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8 * 2**20), b""):
            h.update(bloco)
    return h.hexdigest()


def zipar_pasta(origem, zip_path, prefixo=""):
    with zipfile.ZipFile(zip_path, "w", allowZip64=True) as z:
        for d, _, arqs in os.walk(origem):
            for a in sorted(arqs):
                cheio = os.path.join(d, a)
                nome = prefixo + os.path.relpath(cheio, origem).replace(os.sep, "/")
                modo = zipfile.ZIP_STORED if a.lower().endswith(SEM_COMPRESSAO) else zipfile.ZIP_DEFLATED
                z.write(cheio, nome, compress_type=modo, compresslevel=6)


def dividir(zip_path):
    """Corta o zip em partes .001, .002… quando passa do limite do GitHub. O launcher junta de volta."""
    if os.path.getsize(zip_path) <= PARTE:
        return [zip_path]
    partes = []
    with open(zip_path, "rb") as f:
        n = 1
        while True:
            bloco = f.read(PARTE)
            if not bloco:
                break
            p = f"{zip_path}.{n:03d}"
            with open(p, "wb") as out:
                out.write(bloco)
            partes.append(p)
            n += 1
    return partes


def zipar(cfg):
    v = versao_atual()
    destino = os.path.join(BUILDS, v)
    jogo = os.path.join(destino, "Windows")
    if not os.path.exists(os.path.join(jogo, "NexusRoyale.exe")):
        falhar(f"não achei o jogo empacotado em {jogo}. Rode 'empacotar' antes.")
    for velho in os.listdir(destino):
        if velho.startswith("NexusRoyale-") or velho in ("manifest.json", "notas.md"):
            os.remove(os.path.join(destino, velho))
    zip_jogo = os.path.join(destino, f"NexusRoyale-{v}-Win64.zip")
    print("zipando o jogo…")
    zipar_pasta(jogo, zip_jogo)
    zip_sha, zip_bytes = sha256(zip_jogo), os.path.getsize(zip_jogo)
    partes = dividir(zip_jogo)
    if len(partes) > 1:
        os.remove(zip_jogo)
    instalador = compilar_launcher(os.path.join(destino, INSTALADOR))
    commit = subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    manifest = {
        "jogo": "Nexus Royale",
        "versao": v,
        "config": cfg,
        "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "commit": commit,
        "zip": os.path.basename(zip_jogo),
        "zip_bytes": zip_bytes,
        "zip_sha256": zip_sha,
        "partes": [{"nome": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": sha256(p)} for p in partes],
        # O launcher instalado se troca por este quando a versão daqui for maior que a dele.
        "launcher": {"nome": INSTALADOR, "versao": versao_launcher(), "bytes": os.path.getsize(instalador),
                     "sha256": sha256(instalador)},
    }
    with open(os.path.join(destino, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"zip: {zip_bytes / 2**20:.0f} MB em {len(partes)} parte(s); manifest.json gravado em {destino}")


# --- publicar -----------------------------------------------------------------------------------

def release_existe(v):
    r = subprocess.run(["gh", "release", "view", f"v{v}", "--repo", REPO], capture_output=True, text=True)
    return r.returncode == 0


def publicar(cfg):
    v = versao_atual()
    destino = os.path.join(BUILDS, v)
    man_path = os.path.join(destino, "manifest.json")
    if not os.path.exists(man_path):
        falhar("falta o manifest.json. Rode 'zipar' antes.")
    with open(man_path, encoding="utf-8") as f:
        man = json.load(f)
    tag = f"v{v}"
    if release_existe(v):
        falhar(f"a Release {tag} já existe. Suba a versão com 'versao X.Y.Z' e empacote de novo.")
    notas = opcao("--notas")
    if not notas:
        notas = os.path.join(destino, "notas.md")
        log = subprocess.run(["git", "-C", RAIZ, "log", "-1", "--format=%h %s"], capture_output=True,
                             text=True).stdout.strip()
        with open(notas, "w", encoding="utf-8") as f:
            f.write(f"Nexus Royale {v} ({cfg}), {man['data'][:10]}.\n\nÚltimo commit: {log}\n\n"
                    f"Para instalar: baixe o {INSTALADOR} e abra. Ele cria o atalho \"Nexus Royale\", que confere "
                    "esta página antes de abrir o jogo e baixa as versões novas sozinho.\n")
    arquivos = [man_path, os.path.join(destino, man["launcher"]["nome"])]
    arquivos += [os.path.join(destino, p["nome"]) for p in man["partes"]]
    # A tag fica no commit do build, se ele já foi enviado; senão, no último commit da main no GitHub.
    alvo = "main"
    head = subprocess.run(["git", "-C", RAIZ, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    no_github = subprocess.run(["git", "-C", RAIZ, "branch", "-r", "--contains", head], capture_output=True,
                               text=True).stdout.strip()
    if no_github:
        alvo = head
    else:
        print(f"aviso: o commit {head[:7]} ainda não foi enviado (git push); a tag {tag} fica na main do GitHub. "
              f"O commit do build está no manifest.json.")
    cmd = ["gh", "release", "create", tag, "--repo", REPO, "--target", alvo,
           "--title", f"Nexus Royale {v}", "--notes-file", notas] + arquivos
    print("publicando", tag, "com", len(arquivos), "arquivos…")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        falhar("o gh release create falhou. Confira 'gh auth status' e se a branch main já foi enviada.")
    print(f"publicada: https://github.com/{REPO}/releases/tag/{tag}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        return
    acao = sys.argv[1]
    cfg = opcao("--config", "Development")
    if cfg not in ("Development", "Shipping"):
        falhar("--config deve ser Development ou Shipping")
    if acao == "versao":
        if len(sys.argv) < 3:
            print("versão atual:", versao_atual())
        else:
            gravar_versao(sys.argv[2])
    elif acao == "compilar":
        compilar(cfg)
    elif acao == "empacotar":
        empacotar(cfg)
    elif acao == "launcher":
        compilar_launcher(os.path.join(LAUNCHER, "bin", INSTALADOR))
    elif acao == "zipar":
        zipar(cfg)
    elif acao == "publicar":
        publicar(cfg)
    elif acao == "tudo":
        nova = opcao("--versao")
        if nova:
            gravar_versao(nova)
        elif release_existe(versao_atual()):
            a, b, c = (int(x) for x in versao_atual().split("."))
            gravar_versao(f"{a}.{b}.{c + 1}")
        empacotar(cfg)
        zipar(cfg)
        publicar(cfg)
    else:
        falhar(f"ação desconhecida: {acao}")


if __name__ == "__main__":
    main()
