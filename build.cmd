@ECHO off

pyinstaller --specpath "dist" --add-data "/src/*;." -n "TelegramDiscordIntegration" -F --uac-admin "src/main.py"