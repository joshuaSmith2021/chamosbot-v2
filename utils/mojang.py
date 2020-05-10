import grequests
import requests

def get_uuid_from_player(names):
    # If names is just a string of one name, convert it to a list
    if type(names) == ''.__class__:
        names = [names]

    url = 'https://api.mojang.com/profiles/minecraft'
    req = requests.post(url, json=names)
    return req.json()


def get_players_from_uuids(uuids):
    # Gets the usernames for each uuid provided
    if type(uuids) == ''.__class__:
        uuids = [uuids]

    urls = [f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}' for uuid in uuids]
    reqs = (grequests.get(u) for u in urls)
    ress = grequests.map(reqs)
    return [x.json() for x in ress]


def get_player_from_uuid(uuid):
    # Gets the player data for a uuid
    url = f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}'
    req = requests.get(url)
    return req.json()
