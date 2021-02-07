import os

database_path = os.getenv('TDI_DATABASE_HOST')
database_name = os.getenv('TDI_DATABASE_NAME')
database_username = os.getenv('TDI_DATABASE_USERNAME')
database_password = os.getenv('TDI_DATABASE_PASSWORD')

telegram_api_key = os.getenv('TDI_TELEGRAM_API_KEY')
discord_api_key = os.getenv('TDI_DISCORD_API_KEY')

if os.name == 'nt':
    temp_dir = os.getenv('TEMP') + '/TDI'
else:
    temp_dir = '/tmp/TDI'