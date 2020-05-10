import os
import sys

import datetime
import json
import re
import requests

from utils import matrix

hypixel_api = json.loads(open('credentials.json').read())['hypixel-api-key']

class PlayerCompare():
    game = None
    game_modes = None

    def __build_table(self):
        datasets = self.datasets
        stats = self.stats
        ratios = self.ratios
        table = matrix.Table(just='right')
        mode_name = ''

        if self.game_mode is not None and self.game_modes is not None and self.game_mode in [x[0] for x in self.game_modes]:
            mode = self.game_mode
            mode_position, mode_name = [x for x in self.game_modes if x[0] == self.game_mode][0][1:]
            mode_name += ' '
            new_stats = []
            for stat in stats:
                key = stat['key_name']
                if key[0] == '!':
                    # ! means that this stat should not be shown in
                    #   a specific gamemode table, so do not include
                    #   it in the final table
                    continue
                elif key[0] == '?':
                    new_stats.append({'key_name': '_'.join([mode, key[1:]] if mode_position == 'prefix' else [key[1:], mode]), 'display': stat['display']})
            stats = new_stats

            new_ratios = []
            for ratio in ratios:
                terms = ratio['calculate'].split()
                final_expression = []
                for term in terms:
                    if term[0] == '?':
                        final_expression.append('_'.join([mode, term[1:]] if mode_position == 'prefix' else [term[1:], mode]))
                    else:
                        final_expression.append(term)

                new_ratios.append({'calculate': ' '.join(final_expression), 'display': ratio['display'], 'position': ratio['position']})
            ratios = new_ratios
        else:
            new_stats = []
            for stat in stats:
                key = re.sub('[\?!\.]', '', stat['key_name'])
                new_stats.append({'key_name': key, 'display': stat['display']})
            stats = new_stats

            new_ratios = []
            for ratio in ratios:
                new_ratios.append({'calculate': re.sub('[\?!]', '', ratio['calculate']), 'display': ratio['display'], 'position': ratio['position']})
            ratios = new_ratios

        game_name = mode_name + self.game

        # Construct basic table, but make every entry a string
        table.append(list(map(str, [game_name] + self.igns)))
        for stat in stats:
            table.append([stat['display']] + list(map(lambda x: str(x.get(stat['key_name'], 0)), datasets)))

        if ratios is not None:
            for ratio in ratios:
                new_row = [ratio['display']]
                for dataset in datasets:
                    # Substitute in the actual values for calculation using re.sub
                    expression = re.sub(r'[A-z_][A-z0-9_]+', lambda x: str(dataset[x.group(0)]) if x not in [y for y in dir(__builtins__)] else x, ratio['calculate'])
                    # Use python eval and add the element to the list
                    new_row.append(str(round(eval(expression) * 1000) / 1000))

                # This bit is a little complicated, but I use zip(*table)[0] to get a list of the
                #   row titles, then I get the index of the correct row and add 1 to it in order
                #   to insert the new row in the desired position
                table.insert(list(zip(*table))[0].index(ratio['position']) + 1, new_row)

        return str(table if len(self.igns) == 1 else self.__highlight_winners(table))

    def __highlight_winners(self, table):
        specials = self.reverse_stats
        # table is a matrix.Table, specials is a list of stats
        #   where the lower number is better, ie deaths
        for i, row in enumerate(table[1:]):
            best = min(map(float, row[1:])) if row[0] in specials else max(map(float, row[1:]))
            best = re.sub(r'.0$', '', str(best))
            table[i + 1] = ['!!! ' + best if cell == best else cell for cell in row]

        return table

    def __init__(self, igns, apikey=None, game_mode=None):
        if self.game is None:
            raise Exception('Base PlayerCompare class called, no game specified')
        self.igns = igns
        self.datasets = []
        self.datas = []
        self.fails = []
        self.game_mode = game_mode
        for ign in igns:
            self.datas.append(requests.get('https://api.hypixel.net/player?key={0}&name={1}'.format(hypixel_api if apikey is None else apikey, ign)).json())

        # Validate data, and delete any datasets that had an invalid username
        bad_data = []
        for i, dataset in enumerate(self.datas):
            if dataset['success'] is False:
                bad_data.append(self.igns[i])
            elif dataset['player'] is None:
                bad_data.append(self.igns[i])

        for bad_name in bad_data:
            bad_index = self.igns.index(bad_name)
            del self.igns[bad_index]
            del self.datas[bad_index]
            self.fails.append(bad_name)

        # Build datasets
        for i, data in enumerate(self.datas):
            dataset = data
            for key in self.keys:
                dataset = dataset[key]
            self.datasets.append(dataset)

    def __str__(self):
        table = self.__build_table()
        fail_string = '\n* KPG = Kills per Game\n* FKPG = Final Kills per Game' if self.game == 'Bedwars' else ''
        if len(self.fails) > 0:
            fail_string = '\n\nNo data found for the following player{0}: {1}'.format('s' if len(self.fails) > 1 else '', ', '.join(self.fails))
            fail_string += '\nTry checking the spelling of the name'
        return '{0}{1}'.format(str(table), fail_string)

    def export(self, to_json=True):
        return json.dumps(self.datas) if to_json is True else self.datas


class Bedwars(PlayerCompare):
    game = 'Bedwars'
    keys = ['player', 'stats', 'Bedwars']
    game_modes = [('eight_one', 'prefix', 'Solo'), ('eight_two', 'prefix', 'Doubles'), ('four_three', 'prefix', 'Threes'),
                  ('four_four', 'prefix', '4v4v4v4'), ('two_four', 'prefix', '4v4')]

    ratios = [
                    {
                        'display'  : 'KDR',
                        'calculate': '?kills_bedwars / ?deaths_bedwars',
                        'position' : 'Final Deaths'
                    }, {
                        'display'  : 'Win %',
                        'calculate': '?wins_bedwars / ?games_played_bedwars * 100',
                        'position' : 'Games Played'
                    }, {
                        'display'  : 'Final KDR',
                        'calculate': '?final_kills_bedwars / ?final_deaths_bedwars',
                        'position' : 'KDR'
                    }, {
                        'display'  : 'KPG',
                        'calculate': '?kills_bedwars / ?games_played_bedwars',
                        'position' : 'Beds Broken'
                    }, {
                        'display'  : 'FKPG',
                        'calculate': '?final_kills_bedwars / ?games_played_bedwars',
                        'position' : 'KPG'
                    }
            ]

    stats  = [
                {
                    'key_name': '!eight_one_wins_bedwars',
                    'display': 'Solo Wins'
                }, {
                    'key_name': '!eight_two_wins_bedwars',
                    'display': 'Duos Wins'
                }, {
                    'key_name': '!four_three_wins_bedwars',
                    'display': 'Trios Wins'
                }, {
                    'key_name': '!four_four_wins_bedwars',
                    'display': '4v4v4v4 Wins'
                }, {
                    'key_name': '!two_four_wins_bedwars',
                    'display': '4v4 Wins'
                }, {
                    'key_name': '?wins_bedwars',
                    'display': 'Total Wins'
                }, {
                    'key_name': '?games_played_bedwars',
                    'display': 'Games Played'
                }, {
                    'key_name': '?kills_bedwars',
                    'display': 'Kills'
                }, {
                    'key_name': '?deaths_bedwars',
                    'display': 'Deaths'
                }, {
                    'key_name': '?final_kills_bedwars',
                    'display': 'Final Kills'
                }, {
                    'key_name': '?final_deaths_bedwars',
                    'display': 'Final Deaths'
                }, {
                    'key_name': '?beds_broken_bedwars',
                    'display': 'Beds Broken'
		}
            ]
    reverse_stats = ['Deaths', 'Final Deaths']


class Skywars(PlayerCompare):
    game = 'Skywars'
    keys = ['player', 'stats', 'SkyWars']
    game_modes = [('solo', 'suffix', 'Solo'), ('team', 'suffix', 'Team'), ('mega', 'suffix', 'Mega'),
                  ('solo_normal', 'suffix', 'Solo Normal'), ('solo_insane', 'suffix', 'Solo Insane'),
                  ('team_normal', 'suffix', 'Team Normal'), ('team_insane', 'suffix', 'Team Insane'),
                  ('mega_normal', 'suffix', 'Mega Normal'), ('ranked', 'suffix', 'Ranked'),
                  'ranked_normal', 'suffix', 'Ranked Normal']

    ratios = [
                {
                    'display'  : 'KDR',
                    'calculate': '?kills / ?deaths',
                    'position' : 'Deaths'
                }, {
                    'display'  : 'Win %',
                    'calculate': '?wins / ?losses * 100',
                    'position' : 'Games Played'
                }
        ]

    stats  = [
                {
                    'key_name': '!wins_solo',
                    'display': 'Solo Wins'
                }, {
                    'key_name': '!wins_team',
                    'display': 'Team Wins'
                }, {
                    'key_name': '!wins_mega',
                    'display': 'Mega Wins'
                }, {
                    'key_name': '!wins_ranked',
                    'display': 'Ranked Wins'
                }, {
                    'key_name': '?wins',
                    'display': 'Total Wins'
                }, {
                    'key_name': '?games',
                    'display': 'Games Played'
                }, {
                    'key_name': '?kills',
                    'display': 'Kills'
                }, {
                    'key_name': '?deaths',
                    'display': 'Deaths'
                }
            ]

    reverse_stats = ['Deaths']


class Pit(PlayerCompare):
    game = 'Pit'
    keys = ['player', 'stats', 'Pit', 'pit_stats_ptl']
    ratios = [
                {
                    'display'  : 'KDR',
                    'calculate': 'kills / deaths',
                    'position': 'Deaths'
                }, {
                    'display'  : 'K+A DR',
                    'calculate': '(kills + assists) / deaths',
                    'position' : 'KDR'
                }
        ]

    stats = [
                {
                    'key_name': 'playtime_minutes',
                    'display': 'Minutes'
                }, {
                    'key_name': 'kills',
                    'display': 'Kills'
                }, {
                    'key_name': 'assists',
                    'display': 'Assists'
                }, {
                    'key_name': 'deaths',
                    'display': 'Deaths'
                }, {
                    'key_name': 'max_streak',
                    'display': 'Best Streak'
                }
        ]

    reverse_stats = ['Deaths']


# ================================================ #
# Below is focused on keeping logs of player stats #
# over time. It uses the above classes to fetch    #
# data, and then updates a local directory.        #
# ================================================ #

def get_fields(data):
    # Stats to track:
    stats = {
                'player stats Bedwars': ['wins_bedwars', 'kills_bedwars', 'deaths_bedwars',
                                         'final_kills_bedwars', 'final_deaths_bedwars',
                                         'games_played_bedwars']
        }

    result = {}

    for key, fields in stats.items():
        current = {}
        indexes = key.split()
        dataset = data
        for i in indexes:
            dataset = dataset[i]

        for field in fields:
            current[field] = dataset[field]

        result[indexes[-1]] = current

    return result


def timestrings(today):
    one_day = datetime.timedelta(days=1)

    # Getting the strings for the hour and yesterday are pretty simple
    hour = today.strftime('%Y%m%d-%H0000')
    yesterday = (today - one_day).strftime('%Y%m%d')

    # Get string for last month
    first = today.replace(day=1)
    last_month = (first - one_day).strftime('%Y%m')
    return (hour, yesterday, last_month)


if __name__ == '__main__':
    # path to directory where data is stored
    # While testing, leave as none
    data_dir = '/home/pi/hypixel-player-data'
    # data_dir = None

    if sys.argv[-1] == 'INITIALIZE':
        data_directory = '/home/pi/chamosbot/hypixel-player-data' if data_dir is None else data_dir
        data_path = '{0}/data.json'.format(data_directory)
        current_data = json.loads(open(data_path).read())
        # Build individual json files for each hour; make a maximum of 48
        for date in filter(lambda x: re.match('^[0-9]{8}-[0-2][0-9]0000$', x), current_data.keys()):
            with open('{1}/{0}.json'.format(date, data_directory), 'w') as data_file:
                data_file.write(json.dumps(current_data[date]))

    elif sys.argv[-1] == 'BUILD':
        # Build files for the last 24 hours, 48 hours, 14 days, 7 days,
        # and monthly records
        data_directory = '/home/pi/chamosbot/hypixel-player-data' if data_dir is None else data_dir
        hourly_files = list(filter(lambda x: re.match('^[0-9]{8}-[0-2][0-9]0000.json$', x), os.listdir(data_directory)))
        hourly_files.sort(reverse=True)

        daily_files = list(filter(lambda x: re.match('^[0-9]{8}.json$', x), os.listdir(data_directory)))
        daily_files.sort(reverse=True)

        # Get a list of files from midnight
        midnight_files = filter(lambda x: re.match(r'^[0-9]{8}-0{6}.json$', x), hourly_files)
        for day in midnight_files:
            day_name = day[:8]
            with open('{1}/{0}.json'.format(day_name, data_directory), 'w') as current_file:
                current_file.write(open('{1}/{0}'.format(day, data_directory)).read())

        datasets = {'today': hourly_files[:24], 'twodays': hourly_files[:48], 'thisweek': daily_files[:7], 'twoweeks': daily_files[:14], 'thismonth': daily_files[:30]}

        for file_name, dataset in datasets.items():
            final_data = {}
            for timestamp in dataset:
                final_data[timestamp.replace('.json', '')] = json.loads(open('{1}/{0}'.format(timestamp, data_directory)).read())

            with open('{1}/{0}.json'.format(file_name, data_directory), 'w') as current_file:
                current_file.write(json.dumps(final_data))

    elif sys.argv[-1] == 'CLEAN':
        # Eventually, this will delete old files
        data_directory = '/home/pi/chamosbot/hypixel-player-data' if data_dir is None else data_dir
        hourly_files = list(filter(lambda x: re.match('^[0-9]{8}-[0-2][0-9]0000.json$', x), os.listdir(data_directory)))
        hourly_files.sort(reverse=True)
        old_hourly_files = hourly_files[48:]
        for old_file in old_hourly_files:
            os.remove('{1}/{0}'.format(old_file, data_directory))

    elif sys.argv[-1] == 'UPDATE':
        data_directory = '/home/pi/chamosbot/hypixel-player-data' if data_dir is None else data_dir

        # Get names of players to record stats for
        usernames = sys.argv[1:-1]
        # Get strings representing the timestamp for this data, yesterday's data, and week-old data
        hour = timestrings(datetime.datetime.now())[0]

        data = list(map(get_fields, Bedwars(usernames).export(to_json=False)))

        players = list(map(lambda x: {x[0].lower(): x[1]}, zip(usernames, data)))

        result = {}
        for player in players:
            ign, stats = list(player.items())[0]
            result[ign] = stats

        with open('{1}/{0}.json'.format(hour, data_directory), 'w') as data_file:
            data_file.write(json.dumps(result))
    elif sys.argv[-1] == 'API':
        print(bw(['parcerx'], game_mode='eight_one'))
        print(bw(['parcerx'], game_mode='two_four'))
