import sys
import threading
from typing import Optional

from discord.ext import commands
from discord.ext import tasks

import db, time, config
import discord
import random
import string
import telebot
from threading import Thread
import ctypes

key_map = dict()
key_time_map = dict()


__db__ = db.DBConnection()


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


class bcolors:
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
        def help(message):
            self.tbot.send_message(message.chat.id, '''
Write /connect to generate bind code
After this write tdi!connect [code] in discord

Link for discord bot: https://discord.com/api/oauth2/authorize?client_id=742766156741345312&permissions=59392&scope=bot
Created by kim-kostya(https://github.com/kim-kostya)
            ''')

        super()

        @tbot.message_handler(commands=['connect'])
        def on_command(message: telebot.types.Message):
            if self.tbot.get_chat_member(message.chat.id,
                                         message.from_user.id).status == 'administrator' or self.tbot.get_chat_member(
                    message.chat.id, message.from_user.id).status == 'creator':
                code = generate_key(message.chat.id)
                if code != None:
                    self.tbot.send_message(message.chat.id, 'Your code: ' + code)
                else:
                    self.tbot.send_message(message.chat.id, 'Already connected')

        @tbot.message_handler(content_types=['text'])
        def on_message(message: telebot.types.Message):
            dbc = db.DBConnection()
            if not message.from_user.is_bot:
                if not message.text.startswith('/'):
                    channel = dbc.get_discord_channel(message.chat.id)
                    if channel != None:
                        discord_interface.call_message(message.text, message.from_user.username, channel)
                pass

        print(bcolors.OKGREEN + 'DONE' + bcolors.ENDC)

    def send_message(self, message, author, telegram_id):
        self.tbot.send_message(int(telegram_id), '''
By {0}
{1}
        '''.format(author, message))

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
        print(bcolors.OKGREEN + 'DONE' + bcolors.ENDC)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

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
        self.bot = commands.Bot(command_prefix='!')

        @self.bot.event
        async def on_message(message: discord.Message):
            if not message.author.bot:
                if isinstance(message.content, str):
                    if not (message.content.startswith('!') or message.content.startswith('p!') or message.content.startswith('tdi!')):
                        telegram_id = self.__db__.get_telegram_id(message.channel.id)
                        if telegram_id != None:
                            telegram_interface.send_message(message.content, message.author, telegram_id)
                    elif message.content.startswith('tdi!connect'):

                        code = message.content.split(' ')[1]
                        if key_map[code] != None:
                            discord_channel = message.channel.id
                            telegram_id = key_map[code]
                            self.__db__.save_connection(telegram_id, discord_channel)
                            key_map.pop(code)
                            key_time_map.pop(code)
                            response = 'Connected'
                        else:
                            response = 'Invalid code'
                        await self.bot.get_channel(message.channel.id).send(response)
                    elif message.content.startswith('tdi!help'):
                        await self.bot.get_channel(message.channel.id)\
                            .send('', embed=
                        discord.Embed(title='Instructions',
                                      description='Add telegram bot by this link [https://t.me/tdintegration_bot] to '
                                                  'your telegram group. After this action write "/connect" (It '
                                                  'returns connection code, NOTE IT!). At the final write '
                                                  '"tdi!connect <code>"\n\nP.S. For all actions you need to be '
                                                  'admin\nCreated by kim-kostya(https://github.com/kim-kostya)'))
                    elif message.content.startswith('tdi!disconnect'):
                        from_user: discord.Member = message.author
                        guild: discord.guild.Guild = message.guild
                        admin_role = discord.utils.find(lambda r: r.name.lower() == 'admin', guild.roles)
                        if admin_role in from_user.roles:
                            self.__db__.delete_connection_ds(message.channel.id)
                            await message.channel.send(from_user.mention, embed=discord.Embed(description='Disconnected'))
                        else:
                            await message.channel.send(from_user.mention, embed=discord.Embed(description='You don\'t have permission'))


        @self.bot.event
        async def on_ready():
            self.send_message.start()
            self.check_to_close.start()

        print(bcolors.OKGREEN + 'DONE' + bcolors.ENDC)

    @tasks.loop(seconds=0.1)
    async def send_message(self):
        for data in self.msgs_to_send:
            await self.bot.get_channel(int(data['to'])).send('', embed=data['content'])
            self.msgs_to_send.remove(data)

    @tasks.loop(seconds=0.1)
    async def check_to_close(self):
        if self.to_close:
            await self.bot.close()

    def call_message(self, message: str, author: str, channel: str):
        content = discord.Embed(title='By {0}'.format(author), description=message)
        data = {
            'to': channel,
            'content': content
        }
        self.msgs_to_send.append(data)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):

        self.to_close = True

        # thread_id = self.get_id()
        # res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
        #                                                  ctypes.py_object(SystemExit))
        # if res > 1:
        #     ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        #     print('Exception raise failure')

    def run(self) -> None:
        self.__db__ = db.DBConnection()
        self.bot.run(self.token)
        print('Discord bot stopped')
        self.__db__.close()

    def launch(self):
        print('Starting discord bot...', end='\t\t\t\t')
        try:
            self.start()
            print(bcolors.OKGREEN + 'DONE' + bcolors.ENDC)
        except:
            print(bcolors.FAIL + 'FAILED' + bcolors.ENDC)


telegram_interface: TelegramIntegration
discord_interface: DiscordIntegration


def launch():
    telegram_interface.launch()
    discord_interface.launch()


def stop():
    telegram_interface.raise_exception()
    discord_interface.raise_exception()


if __name__ == '__main__':
    telegram_interface = TelegramIntegration(telebot.TeleBot(config.telegram_api_key))
    discord_interface = DiscordIntegration(config.discord_api_key)
    print('Initializing other components...', end='\t')
    key_checker = KeyChecker()
    key_checker.start()
    print(bcolors.OKGREEN + 'DONE' + bcolors.ENDC)
    launch()

    while True:
        cmd_raw = input('>')
        buffer = cmd_raw.split(' ')
        label = buffer[0]
        args = buffer[1:]
        if label == 'status':
            print('Telegram: \t\t\t\t\t\t\t' + (bcolors.OKGREEN + 'Active' + bcolors.ENDC
                                                if telegram_interface.is_alive()
                                                else bcolors.FAIL + 'Inactive' + bcolors.ENDC))
            print('Discord:  \t\t\t\t\t\t\t' + (bcolors.OKGREEN + 'Active' + bcolors.ENDC
                                                if discord_interface.is_alive()
                                                else bcolors.FAIL + 'Inactive' + bcolors.ENDC))
        elif label == 'stop':
            print('Stopping server...')
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
                print(bcolors.FAIL + 'ID must be integer' + bcolors.ENDC)
            except IndexError:
                print(bcolors.FAIL + 'Usage: remove [id]' + bcolors.ENDC)
