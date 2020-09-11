from typing import Optional

import config
import os
import sqlite3


class DBConnection(object):
    global cursor
    global conn

    def __init__(self):
        if not os.path.exists(config.database_path):
            open(config.database_path, 'a').close()

        self.conn = sqlite3.connect(config.database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
CREATE TABLE IF NOT EXISTS server_map(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_channel VARCHAR(256) NOT NULL UNIQUE,
    telegram_id VARCHAR(32) NOT NULL UNIQUE
);
        ''')
        self.conn.commit()

    def get_discord_channel(self, telegram_id: str) -> Optional[str]:
        result = self.cursor.execute(
            'SELECT discord_channel FROM server_map WHERE telegram_id=\'{0}\''.format(telegram_id))
        buffer = result.fetchone()
        if buffer == None:
            return None
        return buffer[0]

    def get_telegram_id(self, discord_channel: str) -> Optional[str]:
        result = self.cursor.execute(
            'SELECT telegram_id FROM server_map WHERE discord_channel=\'{0}\''.format(discord_channel))
        buffer = result.fetchone()
        if buffer == None:
            return None
        return buffer[0]

    def save_connection(self, telegram_id: str, discord_channel: str):
        self.cursor.execute(
            'INSERT INTO server_map(id, discord_channel, telegram_id) VALUES(NULL, \'{0}\', \'{1}\')'.format(
                discord_channel, telegram_id))
        self.conn.commit()

    def delete_connection_tg(self, telegram_id: str):
        self.cursor.execute('DELETE FROM server_map WHERE telegram_id=\'{0}\''.format(telegram_id))
        self.conn.commit()

    def delete_connection_ds(self, discord_channel: str):
        self.cursor.execute('DELETE FROM server_map WHERE discord_channel=\'{0}\''.format(discord_channel))
        self.conn.commit()

    def get_all_connections(self):
        result = self.cursor.execute('SELECT * FROM server_map')
        return result.fetchall()

    def delete_connection_by_id(self, _id: int):
        self.cursor.execute(f'DELETE FROM server_map WHERE id={_id}')
        self.conn.commit()

    def close(self):
        self.conn.close()
