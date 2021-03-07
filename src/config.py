import os

database_driver = 'sqlite'
database_path = os.getenv('TDI_DATABASE_HOST', './database.sqlite')
database_name = os.getenv('TDI_DATABASE_NAME')
database_username = os.getenv('TDI_DATABASE_USERNAME')
database_password = os.getenv('TDI_DATABASE_PASSWORD')

telegram_api_key = os.getenv('TDI_TELEGRAM_API_KEY')
discord_api_key = os.getenv('TDI_DISCORD_API_KEY')

discord_help_message = '''
Add telegram bot by this link [https://t.me/tdintegration_bot] to your telegram group. After this action write "/connect" (It returns connection code, NOTE IT!). At the final write "tdi!connect <code>"

P.S. For all actions you need to be admin
Created by kim-kostya(https://github.com/kim-kostya)
'''
telegram_help_message = '''
Write /connect to generate bind code
After this write tdi!connect [code] in discord

Link for discord bot: https://discord.com/api/oauth2/authorize?client_id=742766156741345312&permissions=59392&scope=bot
Created by kim-kostya(https://github.com/kim-kostya)
'''

if os.name == 'nt':
    temp_dir = os.getenv('TEMP') + '/TDI'
else:
    temp_dir = '/tmp/TDI'