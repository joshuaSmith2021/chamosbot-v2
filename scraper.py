# Workaround to prevent errors with grequests
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import sys
import json
import re

import requests
import grequests
from bs4 import BeautifulSoup

from utils import matrix
from utils import mojang

def format_number(num):
    if int(num) == float(num):
        # It is an integer
        return '{:,}'.format(num)
    else:
        # It is a float:
        return '{:,.2f}'.format(num)


def get_player_pages(igns):
    # Get the Plancke page for each player
    if type(igns) == ''.__class__:
        igns = [igns]

    urls = ['https://plancke.io/hypixel/player/stats/{0}'.format(ign) for ign in igns]
    reqs = (grequests.get(u) for u in urls)
    ress = grequests.map(reqs)
    return [x.text for x in ress]


def get_bw_data(page):
    # Get Bedwars data from their Plancke page
    soup = BeautifulSoup(page, features='html5lib')
    bw_div = soup.find('div', {'id': 'stat_panel_BedWars'})
    bw_table = bw_div.findChild('table')

    table = []
    for row in [x for x in bw_table.descendants if x.name == 'tr'][1:]:
        # for cell in row.children:
        #     print(cell)
        cells = [x for x in row.strings if x != '\n']
        if cells == []:
            continue

        table.append(cells)

    stats = {}
    keys = table[0]
    gamemodes = [x[0] for x in table][1:]
    for row in table[1:]:
        zipped = list(zip(keys, row))
        gamemode = zipped[0][1]
        current = {}
        for key, stat in zipped[1:]:
            if key not in current.keys():
                current[key] = stat
            else:
                current['Final {0}'.format(key)] = stat

        stats[gamemode] = current

    return stats


def get_stat(dataset, stat):
    data = dataset
    for key in stat.split('.'):
        data = data[key]

    return data.replace(',', '')


def make_bw_table(rows, datasets):
    result = matrix.Table(just='right')
    result.append(['Stat'] + [x[0] for x in datasets])

    for stat in rows:
        row = []

        stat_name = '{0[1]} ({0[0]})'.format(re.sub('[$()^]', '', stat).split('.')) if '#' not in stat else stat.split('#')[1]
        row.append(stat_name)

        for username, dataset in datasets:
            # An expression with the variables plugged in
            plugged = re.sub('\^[^^$]+\.[^^$]+\$', lambda x: get_stat(dataset, x.group(0)[1:-1]), stat.split('#')[0])
            try:
                value = format_number(eval(plugged))
            except ZeroDivisionError as err:
                # This exception occurs when a user has 0 deaths or another
                # ratio denominator. K/D will raise a ZeroDivisionError
                value = '-'
            except SyntaxError as err:
                # This exception occurs when a user has 0 in a certain stat,
                # for example 0 kills
                value = '-'
            # data = dataset
            # for key in stat.split('.'):
            #     data = data[key]
            row.append(value)
        result.append(row)

    return result


if __name__ == '__main__':
    uuids = json.loads(open(r'C:\Users\blue\Desktop\Coding\uuids.json').read())
    usernames = [x['name'] for x in mojang.get_players_from_uuids(uuids)] if len(sys.argv) == 1 else sys.argv[1:]
    pages = get_player_pages(usernames)
    datasets = list(zip(usernames, [get_bw_data(page) for page in pages]))

    # datasets = []
    rows = ['^Solo.Wins$ #Solo Wins', '^Doubles.Wins$ #Doubles Wins', '^3v3v3v3.Wins$ #3v3v3v3 Wins', '^4v4v4v4.Wins$ #4v4v4v4 Wins',
            '^4v4.Wins$ #4v4 Wins', '^Overall.Wins$ #Total Wins', '^Overall.Wins$ / (^Overall.Wins$ + ^Overall.Losses$) #Win Rate', '^Overall.Kills$ #Kills', '^Overall.K/D$ #K/D',
            '^Overall.Final Kills$ #Final Kills', '^Overall.Final K/D$ #Final K/D', '^Overall.Kills$ + ^Overall.Final Kills$ #Total Kills']

    # for username in usernames:
    #     data = get_bw_data(username)
    #     datasets.append((username, data))

    # Sort datasets by username
    datasets.sort(key=lambda x: x[0].lower())
    print(make_bw_table(rows, datasets))
