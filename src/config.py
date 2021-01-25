import os

database_path = './database.sqlite'

telegram_api_key = os.getenv('TDI_TELEGRAM_API_KEY')
discord_api_key = os.getenv('TDI_DISCORD_API_KEY')

if os.name == 'nt':
    temp_dir = os.getenv('TEMP') + '/TDI'
else:
    temp_dir = '/tmp/TDI'