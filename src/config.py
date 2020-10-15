import os

database_path = './database.sqlite'

telegram_api_key = os.getenv('TDI_TELEGRAM_API_KEY')
discord_api_key = os.getenv('TDI_DISCORD_API_KEY')

temp_dir = os.getenv('TEMP') + '/TDI'