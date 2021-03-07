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
```remove <id>``` - remove telegram-discord connection \
```stop``` - stop server

## Installing
Install python3 (https://www.python.org/downloads/)

Modules:\
discord.py (```pip install -U discord.py```) \
requests (```pip install -U requests```) \
PyTelegramBotApi (```pip install -U pyTelegramBotAPI```) \
psycopg2 (```pip install -U psycopg2```) Optional

### Windows
Download pyinstaller (```pip install pyinstaller```)

```build.cmd```

### Linux
```chmod +x ./install.sh``` \
```sudo ./install.sh```


## Environment variables
### API KEYS
TDI_TELEGRAM_API_KEY  = [Telegram bot token]\
TDI_DISCORD_API_KEY   = [Discord api token]
### Database (PostgresSQL)
TDI_DATABASE_HOST     = [Database server url]\
TDI_DATABASE_NAME     = [Database name]\
TDI_DATABASE_USERNAME = [Database username]\
TDI_DATABASE_PASSWORD = [Database password]