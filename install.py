params = {
    'TDI_DATABASE_HOST': 'Database url:',
    'TDI_DATABASE_NAME': 'Database name:',
    'TDI_DATABASE_USERNAME': 'Database username:',
    'TDI_DATABASE_PASSWORD': 'Database password:',
    'TDI_TELEGRAM_API_KEY': 'Telegram API key:',
    'TDI_DISCORD_API_KEY': 'Discord API key:'
}

FILE_PATH = '/etc/profile.d/tdi_environment.sh'

final_content = '''
!/bin/bash

'''

if __name__ == '__main__':
    for param in params:
        question = params[param]
        print(question)
        answer = input('>')
        final_content += f'{param}={answer}'

    file_tdi_env = open(FILE_PATH, 'w+')
    file_tdi_env.write(final_content)
    file_tdi_env.close()
