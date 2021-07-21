import json
from json.decoder import JSONDecodeError
import time
import os

import discord
SECONDS_PER_DAY = 86400
# SECONDS_PER_DAY = 1
DATA_FILENAME = 'data.json'
THE_GAME = 'data/the_game.json'
DEFAULT_SETTINGS = {
            "points_for_discussion": 1,
            "points_for_suggestion": 1,
            "points_for_picked_suggestion": 3,
            "time_between_discussions": 1 * SECONDS_PER_DAY,
            "time_between_suggestion": 7 * SECONDS_PER_DAY
}

class GuildData:

    def __init__(self, id, users, discussion_channel, suggestion_channel, settings) -> None:
        self.id = id
        self.users = users
        self.discussion_channel = discussion_channel
        self.suggestion_channel = suggestion_channel
        self.settings = settings

    @staticmethod
    def from_json(json_obj: dict):
        return GuildData(json_obj['id'], 
                            json_obj['users'],
                            json_obj['discussion_channel'],
                            json_obj['suggestion_channel'],
                            json_obj['settings'])

class QotdData:

    def __init__(self) -> None:
        self.data_dir = 'data/guilds'
        try:
            os.makedirs(self.data_dir)
        except FileExistsError:
            pass    

    def _load_guild(self, guild_id: int) -> GuildData:
        path = os.path.join(self.data_dir, f'{guild_id}.json')
        try:
            reader = open(path , 'r')
        except FileNotFoundError:
            return GuildData(guild_id, dict(), None, None, DEFAULT_SETTINGS)
        json_guild = json.loads(reader.read())
        reader.close()
        try:
            return GuildData.from_json(json_guild)
        except JSONDecodeError:
            return GuildData(guild_id, dict(), None, None, DEFAULT_SETTINGS) 
    
    def _save_guild(self, guild: GuildData) -> None:
        path = os.path.join(self.data_dir, f'{guild.id}.json')
        writer = open(path , 'w')
        writer.write(json.dumps(guild, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4))
        writer.close()

    def get_users(self, guild_id: int) -> dict:
        guild_data = self._load_guild(guild_id)
        return guild_data.users

    def get_last_suggestion(self, guild_id: int, user: discord.User, guild_data: GuildData=None) -> dict:
        if guild_data is None:
            guild_data = self._load_guild(guild_id)
        user_info = self._get_user_info(guild_data, user)
        return user_info['last_suggestion']

    def get_last_answer(self, guild_id: int, user: discord.User, guild_data: GuildData=None) -> dict:
        if guild_data is None:
            guild_data = self._load_guild(guild_id)
        user_info = self._get_user_info(guild_data, user)
        return user_info['last_answer']

    def update_user_answer(self, guild_id: int, user: discord.User, message: discord.Message) -> None:
        guild_data = self._load_guild(guild_id)
        last_answer = self.get_last_answer(guild_id, user, guild_data)
        last_answer['time'] = time.time()
        last_answer['content'] = message.content
        guild_data.users[f'{user.id}']['last_answer'] = last_answer
        self._save_guild(guild_data)

    def update_user_suggestion(self, guild_id: int, user: discord.User, message: discord.Message) -> None:
        guild_data = self._load_guild(guild_id)
        last_suggestion = self.get_last_suggestion(guild_id, user, guild_data)
        last_suggestion['time'] = time.time()
        last_suggestion['content'] = message.content
        guild_data.users[f'{user.id}']['last_suggestion'] = last_suggestion
        self._save_guild(guild_data)

    def _get_user_info(self, guild_data: GuildData, user: discord.User) -> dict:
        info = guild_data.users.get(f'{user.id}', None)
        if info is None:
            info = {
                'last_answer': {
                    'time': 0,
                    'content': ''
                },
                'last_suggestion': {
                    'time': 0,
                    'content': ''
                },
                'points': 0
            }
            guild_data.users[f'{user.id}'] = info
        return info

    def get_discussion_channel(self, guild_id: int) -> dict:
        guild_data = self._load_guild(guild_id)
        return guild_data.discussion_channel
    
    def set_discussion_channel(self, guild_id: int, channel_id: int) -> None:
        guild_data = self._load_guild(guild_id)
        guild_data.discussion_channel = channel_id
        self._save_guild(guild_data)

    def get_suggestion_channel(self, guild_id: int) -> dict:
        guild_data = self._load_guild(guild_id)
        return guild_data.suggestion_channel

    def set_suggestion_channel(self, guild_id: int, channel_id: int) -> None:
        guild_data = self._load_guild(guild_id)
        guild_data.suggestion_channel = channel_id
        self._save_guild(guild_data)

    def get_settings_for_guild(self, guild_id: int) -> dict:
        guild_data = self._load_guild(guild_id)
        return guild_data.settings
    
    def set_setting_for_guild(self, guild_id: int, setting_key, setting_value) -> None:
        guild_data = self._load_guild(guild_id)
        guild_data.settings[setting_key] = setting_value
        self._save_guild(guild_data)
    
    def get_user_points(self, guild_id: int, user: discord.User, guild_data: GuildData=None) -> int:
        if guild_data is None:
            guild_data = self._load_guild(guild_id)
        user_info = self._get_user_info(guild_data, user)
        return user_info['points']

    def add_user_points(self, guild_id: int, user: discord.User, points_to_add: int) -> None:
        guild_data = self._load_guild(guild_id)
        points = self.get_user_points(guild_id, user, guild_data)
        points += points_to_add
        guild_data.users[f'{user.id}']['points'] = points
        self._save_guild(guild_data)

    def get_the_game_channels(self) -> set:
        try:
            reader = open(THE_GAME, 'r')
            channels = json.loads(reader.read())
        except (FileNotFoundError, JSONDecodeError) as e:
            channels = []
        finally:
            reader.close()
        return set(channels)
    
    def add_the_game_channel(self, channel_id) -> None:
        writer = open(THE_GAME, 'w')
        channels = list(self.get_the_game_channels())
        channels.append(channel_id)
        writer.write(json.dumps(channels, indent=4))
        writer.close()