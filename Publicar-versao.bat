@echo off
rem Publica uma versao nova do Nexus Royale no GitHub Releases (a Unreal precisa estar FECHADA).
rem Sobe o numero da versao, empacota, zipa e cria a Release. Os launchers instalados baixam na proxima abertura.
rem Opcoes: --versao X.Y.Z  --config Shipping  --notas arquivo.md
cd /d "%~dp0"
python -I Unreal\ue_release.py tudo %*
pause
