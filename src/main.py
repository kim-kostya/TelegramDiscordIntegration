import ctypes
import random
import string
import sys
import threading
import os
import requests
from threading import Thread
from typing import Optional
import datetime
import tracemalloc
import asyncio

import discord
import telebot
from discord.ext import commands
from discord.ext import tasks

import config
import db
import time

key_map = dict()
key_time_map = dict()

__db__ = db.DBConnection()


class Logger:
    use_cli = False
    log_file = None

    def __init__(self):
        try_create_dir("./logs")
        self.log_file = open(f"./logs/log-{datetime.datetime.now()}.txt", "w+")

    def log(self, message):
        final_message = f"[{datetime.datetime.now()}]{message}"
        self.log_file.write(final_message)
        if self.use_cli:
            print(final_message)


def generate_key(telegram_id: str) -> Optional[str]:
    __db__ = db.DBConnection()
    if __db__.get_telegram_id(telegram_id) is None:
        if telegram_id in key_map.values():
            for key, val in key_map.items():
                if val == telegram_id:
                    key_map.pop(key)
                    key_time_map.pop(key)
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(5))
        if key_map.keys().__contains__(result_str):
            return generate_key(telegram_id)
        key_map[result_str] = telegram_id
        key_time_map[result_str] = 300
        return result_str
    else:
        return None


def generate_str() -> str:
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(5))
    return result_str


def try_create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


class KeyChecker(Thread):
    tostop = False

    def run(self):
        while True:
            if self.tostop:
                break
            for _key in key_time_map:
                time_ = key_time_map[_key]
                time_ -= 1
                if time_ <= 0:
                    key_map.pop(_key)
                    key_time_map.pop(_key)
            time.sleep(1)

    def stop(self):
        self.tostop = True


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TelegramIntegration(Thread):
    tbot: telebot.TeleBot
    __db__: db.DBConnection

    def __init__(self, tbot: telebot.TeleBot):
        super().__init__()
        print('Initializing telegram bot...', end='\t\t')
        self.tbot = tbot

        @tbot.message_handler(commands=['start', 'help'])
        def on_help_command(message):
            self.tbot.send_message(message.chat.id, text=config.telegram_help_message)

        @tbot.message_handler(commands=['connect'])
        def on_connect_command(message: telebot.types.Message):
            if self.tbot.get_chat_member(message.chat.id, message.from_user.id).status == 'administrator' or 'creator':

                code = generate_key(message.chat.id)

                if code is not None:
                    self.tbot.send_message(message.from_user.id, 'Your code: ' + code)
                    self.tbot.send_message(message.chat.id, 'Code sent')
                else:
                    self.tbot.send_message(message.chat.id, 'Already connected')

        @tbot.message_handler(content_types=['text'])
        def on_message(message: telebot.types.Message):
            dbc = db.DBConnection()
            if not message.from_user.is_bot:
                if not message.text.startswith('/'):
                    channel = dbc.get_discord_channel(message.chat.id)
                    if channel is not None:
                        discord_interface.call_send_text(message.text, message.from_user.username, channel)
                pass

        @tbot.message_handler(content_types=['photo', 'document', 'audio'])
        def on_media(message: telebot.types.Message):
            dbc = db.DBConnection()
            if not message.from_user.is_bot:
                if message.photo is None:
                    received_images = None
                else:
                    received_images = message.photo[1::2]

                channel = dbc.get_discord_channel(message.chat.id)

                if message.text is None:
                    message.text = ''

                try_create_dir(f"{config.temp_dir}/telegram/photos")
                try_create_dir(f"{config.temp_dir}/telegram/videos")
                try_create_dir(f"{config.temp_dir}/telegram/documents")

                self.__send_media_list__(received_images, message.from_user.username, channel, msg=message.text)
                self.__send_media__(message.document, message.from_user.username, channel, msg=message.text)
                self.__send_media__(message.audio, message.from_user.username, channel, msg=message.text)

        print(ConsoleColors.OKGREEN + 'DONE' + ConsoleColors.ENDC)

    def __send_media_list__(self, media, username, channel, msg=''):
        if media is None:
            return
        for file in media:
            self.__send_media__(file, username, channel, msg)

    def __send_media__(self, media, username, channel, msg=''):
        if media is None:
            return

        if media.file_size > 2000000:
            return

        file_path = self.tbot.get_file(media.file_id).file_path

        response = requests.get(f"https://api.telegram.org/file/bot{config.telegram_api_key}/{file_path}")
        fp = open(f"{config.temp_dir}/{file_path}", "wb+")
        fp.write(response.content)
        fp.close()

        if channel is not None:
            discord_interface \
                .call_send_file(msg, f"{config.temp_dir}/telegram/{file_path}",
                                username, channel)

    def send_message(self, message, author, telegram_id):
        self.tbot.send_message(int(telegram_id), '''
By {0}
{1}
        '''.format(author, message))

    def send_file(self, telegram_id, file, author):
        self.tbot.send_document(int(telegram_id), open(file, 'rb').read())

    def run(self):
        self.__db__ = db.DBConnection()
        try:
            self.tbot.polling()
        except SystemExit:
            pass
        finally:
            print('Telegram bot stopped')
            self.__db__.close()

    def launch(self):
        print('Starting telegram bot...', end='\t\t\t')
        self.start()
        print(ConsoleColors.OKGREEN + 'DONE' + ConsoleColors.ENDC)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for thread_id, thread in threading._active.items():
            if thread is self:
                return thread_id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class DiscordIntegration(Thread):
    bot: commands.Bot
    token: str
    __db__: db.DBConnection
    msgs_to_send = list()
    to_close = False

    def __init__(self, token: str):
        super().__init__()
        print('Initializing discord bot...', end='\t\t\t')
        self.token = token
        self.bot = commands.Bot(command_prefix='tdi!')

        @self.bot.event
        async def on_message(message: discord.Message):
            if not message.author.bot:
                if isinstance(message.content, str):
                    if not (message.content.startswith('!')
                            or message.content.startswith('p!')
                            or message.content.startswith('tdi!')):
                        telegram_id = self.__db__.get_telegram_id(message.channel.id)
                        if telegram_id is not None:
                            for file in message.attachments:
                                self.__send_media__(telegram_id, file, message.author)
                            telegram_interface.send_message(message.content, message.author, telegram_id)
                    elif message.content.startswith('tdi!connect'):
                        code = message.content.split(' ')[1]
                        if key_map[code] is not None:
                            discord_channel = message.channel.id
                            telegram_id = key_map[code]
                            self.__db__.save_connection(telegram_id, discord_channel)
                            key_map.pop(code)
                            key_time_map.pop(code)
                            response = 'Connected'
                        else:
                            response = 'Invalid code'
                        await message.channel.send(message.author.mention, embed=discord.Embed(description=response))
                    elif message.content.startswith('tdi!help'):
                        await self.bot\
                            .get_channel(message.channel.id)\
                            .send('',
                                  embed=discord.Embed(title='Instructions', description=config.discord_help_message))
                    elif message.content.startswith('tdi!disconnect'):
                        from_user: discord.Member = message.author
                        guild: discord.guild.Guild = message.guild
                        admin_role = discord.utils.find(lambda r: r.name.lower() == 'admin', guild.roles)
                        if admin_role in from_user.roles:
                            self.__db__.delete_connection_ds(message.channel.id)
                            await message.channel\
                                .send(from_user.mention, embed=discord.Embed(description='Disconnected'))
                        else:
                            await message.channel\
                                .send(from_user.mention, embed=discord.Embed(description='You don\'t have permission'))

        @self.bot.event
        async def on_ready():
            self.send_messages.start()
            self.check_to_close.start()
            print(ConsoleColors.OKGREEN + 'DONE' + ConsoleColors.ENDC)

        print(ConsoleColors.OKGREEN + 'DONE' + ConsoleColors.ENDC)

    @staticmethod
    def __send_media__(to, file, author):
        try_create_dir(f"{config.temp_dir}/discord/{file.id}")

        response = requests.get(file.url)
        fp = open(f"{config.temp_dir}/discord/{file.id}/{file.filename}", "wb+")
        fp.write(response.content)
        fp.close()

        telegram_interface.send_file(to, f"{config.temp_dir}/discord/{file.id}/{file.filename}", author)

    @tasks.loop(seconds=0.1)
    async def send_messages(self):
        for msg in self.msgs_to_send:
            file: discord.file.File = None
            if 'file' in msg:
                fp = open(msg['file'], "rb+")
                file = discord.file.File(fp)
            await self.bot.get_channel(int(msg['to'])).send('', embed=msg['content'], file=file)
            self.msgs_to_send.remove(msg)

    @tasks.loop(seconds=0.1)
    async def check_to_close(self):
        if self.to_close:
            await self.bot.close()

    def call_send_text(self, message: str, author: str, channel: str):
        content = discord.Embed(title='By {0}'.format(author), description=message)
        data = {
            'to': channel,
            'content': content,
        }
        self.msgs_to_send.append(data)

    def call_send_file(self, message: str, file: str, author: str, channel: str):
        content = discord.Embed(title='By {0}'.format(author), description=message)
        data = {
            'to': channel,
            'content': content,
            'file': file
        }

        self.msgs_to_send.append(data)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for thread_id, thread in threading._active.items():
            if thread is self:
                return thread_id

    def run(self) -> None:
        self.bot.login(token=self.token)
        self.bot.start(self.token)

    def raise_exception(self):

        self.to_close = True

        # thread_id = self.get_id()
        # res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
        #                                                  ctypes.py_object(SystemExit))
        # if res > 1:
        #     ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        #     print('Exception raise failure')

    def launch(self):
        print('Starting discord bot...', end='\t\t\t\t')
        try:
            self.__db__ = db.DBConnection()
            # self.start()
            self.bot.run(self.token)
        except:
            print(ConsoleColors.FAIL + 'FAILED' + ConsoleColors.ENDC)


class ConsoleThread(Thread):

    def run(self) -> None:

        if '--cli' in sys.argv:
            while True:
                cmd_raw = input()

                buffer = cmd_raw.split(' ')
                label = buffer[0]
                args = buffer[1:]

                if label == 'status':
                    print('Telegram: \t\t\t\t\t\t\t' + (ConsoleColors.OKGREEN + 'Active' + ConsoleColors.ENDC
                                                        if telegram_interface.is_alive()
                                                        else ConsoleColors.FAIL + 'Inactive' + ConsoleColors.ENDC))
                    print('Discord:  \t\t\t\t\t\t\t' + (ConsoleColors.OKGREEN + 'Active' + ConsoleColors.ENDC
                                                        if discord_interface.bot.is_ready()
                                                        else ConsoleColors.FAIL + 'Inactive' + ConsoleColors.ENDC))
                elif label == 'stop':
                    print('Stopping server...')
                    clear_temp_dir()
                    stop()
                    key_checker.stop()
                    sys.exit(0)
                elif label == 'keymap':
                    print('KEY   | Telegram ID | Time')
                    print('==========================')
                    for key in key_map:
                        print(key + ' | ' + str(key_map[key]) + '  | ' + str(key_time_map[key]))
                    print('==========================')
                elif label == 'connections':
                    print('Shape: [Telegram ID <===> Discord ID]')
                    for connection in __db__.get_all_connections():
                        print(f'[{connection[0]}] {connection[2]} <===> {connection[1]}')
                elif label == 'remove':
                    try:
                        _id = int(args[0])
                        __db__.delete_connection_by_id(_id)
                        print('REMOVED')
                    except ValueError:
                        print(ConsoleColors.FAIL + 'ID must be integer' + ConsoleColors.ENDC)
                    except IndexError:
                        print(ConsoleColors.FAIL + 'Usage: remove [id]' + ConsoleColors.ENDC)


telegram_interface: TelegramIntegration
discord_interface: DiscordIntegration
console_thread: ConsoleThread


def launch():
    telegram_interface.launch()
    console_thread.start()
    discord_interface.launch()


def stop():
    telegram_interface.raise_exception()
    discord_interface.raise_exception()


def clear_dir(path):
    for file in os.listdir(path):
        os.remove(file)


def clear_temp_dir():
    for file in os.listdir(config.temp_dir):
        os.remove(config.temp_dir+'/'+file)


if __name__ == '__main__':
    try_create_dir(config.temp_dir)
    try_create_dir(f'{config.temp_dir}/telegram')
    try_create_dir(f'{config.temp_dir}/discord')

    telegram_interface = TelegramIntegration(telebot.TeleBot(config.telegram_api_key))
    discord_interface = DiscordIntegration(config.discord_api_key)

    print('Initializing other components...', end='\t')
    key_checker = KeyChecker()
    key_checker.start()
    console_thread = ConsoleThread()
    print(ConsoleColors.OKGREEN + 'DONE' + ConsoleColors.ENDC)

    launch()
