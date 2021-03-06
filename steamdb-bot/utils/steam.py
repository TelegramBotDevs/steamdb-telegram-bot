import logging

import requests
from steamdbparser import SteamDbParser

from . import database
from . import settings


class Steam:
    def __init__(self):
        self.steamdb = SteamDbParser.parser()
        self.db = database.DB()

    def is_steam_id(self, steam_id):
        return self.steamdb.isSteamId(steam_id)

    def get_steamdb_profile(self, steam_id):
        logging.info(f'Looking up {steam_id} in cache')
        data = self.db.get_cache(f'steamdb:{steam_id}')
        if data:
            logging.info(f'Returning cache of {steam_id}')
            return data
        else:
            logging.info(f'Not in cache, fetching.')
            data = self.steamdb.getSteamDBProfile(steam_id)
            if data:
                logging.info(f'Setting cache for {steam_id}')
                self.db.set_cache(f'steamdb:{steam_id}', data)
                return data

    def get_steam_id(self, username):
        steam_id = None
        try:
            r = requests.get(
                f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={settings.STEAM_API_TOKEN}&vanityurl={username}',
                timeout=(2, 10))
            if r.status_code == 200:
                data = r.json()['response']
                if data['success'] == 1:
                    steam_id = data['steamid']
        except Exception:
            logging.exception(f'Something happened while fetching "{username}" steam_id')
        finally:
            return steam_id

    def get_steam_profile(self, steam_id):
        try:
            r = requests.get(
                f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={settings.STEAM_API_TOKEN}&steamids={steam_id}',
                timeout=(2, 10))
            if r.status_code == 200:
                data = r.json()['response']['players'][0]
                if data['personaname']:
                    return {'username': data['personaname'], 'profile': data['profileurl'], 'img': data['avatarfull']}
            return None
        except Exception:
            logging.exception(f'Something happened while fetching "{steam_id}" profile data')
            return None
