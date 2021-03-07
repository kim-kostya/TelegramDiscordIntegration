import install

params_postgres = {
    'TDI_DATABASE_HOST': 'Database url:',
    'TDI_DATABASE_NAME': 'Database name:',
    'TDI_DATABASE_USERNAME': 'Database username:',
    'TDI_DATABASE_PASSWORD': 'Database password:'
}

params_sqlite = {
    'TDI_DATABASE_HOST': 'Database path:'
}

params_default = {
    'TDI_TELEGRAM_API_KEY': 'Telegram API key:',
    'TDI_DISCORD_API_KEY': 'Discord API key:'
}

FILE_PATH = '/etc/profile.d/tdi_environment.sh'

final_content = '''
#!/bin/bash

'''


def set_params(params):
    for param in params:
        question = params[param]
        print(question)
        answer = input('>')
        install.final_content += f'{param}={answer}\nexport {param}\n'


def choose_menu(message, answers):
    print(message)
    for answer_id in range(len(answers)):
        print(f'[{answer_id}] {answers[answer_id]}')

    _id = input('Choose one [Default:0]: ')
    if _id == '':
        _id = 0
    return answers[int(_id)]


if __name__ == '__main__':
    set_params(params_default)

    database_type = choose_menu('Choose database', [
        'Sqlite',
        'Postgres'
    ])

    if database_type == 'Sqlite':
        set_params(params_sqlite)
    elif database_type == 'Postgres':
        set_params(params_postgres)

    file_tdi_env = open(FILE_PATH, 'w+')
    file_tdi_env.write(install.final_content)
    file_tdi_env.close()
