# TelegramDiscordIntegration
This bot can easy merge text chat in your discord server with your telegram group

## Bots
Telegram: https://t.me/tdintegration_bot \
Discord: https://discord.com/oauth2/authorize?client_id=742766156741345312&permissions=59392&scope=bot

## How to connect
+ Add telegram bot to group
+ Open group
+ Write ```/connect```. It returns connection code, note one.
+ Add discord bot to server
+ Open text channel which you want to merge with your telegram group 
+ Write ```tdi!connect <code>```

## Commands (Telegram)
```/help``` - print instructions\
```/connect``` - generate special code\
```/disconnect``` - remove connection with discord

## Commands (Discord)
```tdi!help``` - print instructions\
```tdi!connect <code>``` - connect discord\
```tdi!disconnect``` - remove connection with telegram

## Commands (Server console)
```status``` - print bots' connections status\
```connections``` - print lost of telegram-discord connections\

## Build from sources
Install python3 (https://www.python.org/downloads/)

Modules:\
discordpy (```pip install -U discord.py```) \
PyTelegramBotApi (```pip install pyTelegramBotAPI```) \
\
Download pyinstaller (```pip install pyinstaller```)

### On Windows
run ```build.cmd```
### On Linux
run ```build.sh```