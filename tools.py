import requests
import re
import random
import json
import datetime

import hypixel
import stat_classes

discord_secret = json.loads(open('credentials.json').read())['discord-token']
website_link = 'https://chamosbotonline.herokuapp.com'

def get_guild(gid, fields=None):
    url = 'https://discordapp.com/api/guilds/{0}'.format(gid)
    headers = {'Authorization': 'Bot {0}'.format(discord_secret)}
    req = requests.get(url, headers=headers)
    parsed = req.json()
    return parsed if fields is None else [parsed[x] for x in fields]


def log(text):
    print('{0}: {1}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H%M%S'), text))


async def send_help_message(message, bot):
    await message.channel.send('For a list of commands and command reference, visit {0} and go to the FEATURES tab.'.format(website_link))


async def get_game_stats(message, bot):
    # await message.channel.send('Sorry, this command is under development at the moment, so this command might not work')

    # Message should be !stats [bedwars|skywars|pit] ign ign ign
    games = ['bedwars', 'skywars', 'pit', 'bw', 'sw']
    game_string = 'Oops, looks like the game you asked for is invalid! {0} are available'.format(', '.join(games))
    log('Stats requested with "{0}"'.format(message.content))
    parameters = message.content.split()[1:]
    usernames = [x for x in parameters[1:] if x[0] != '-']
    flags = [x[1:] for x in parameters[1:] if x[0] == '-']

    try:
        api_key = random.choice(json.loads(open('credentials.json').read())['hypixel-api-keys'][str(message.guild.id)])[0]
    except KeyError as err:
        await message.channel.send('It looks like your server does not have a Hypixel API key connected! Please use command `!addkey` to get connected!')
        log('{0} did not have an API key connected'.format(message.guild))
        return
    except AttributeError as err:
        # Currently just ignoring this error, as the skywars stats and pit stats
        # are not supported
        pass

    game = parameters[0]
    game_mode = None if flags == [] else flags[-1]
    log('Game: {1}; Usernames: {0}'.format(', '.join(usernames), game))

    stats_page = 'http://chamosbotonline.herokuapp.com/bedwars?igns={0}'.format('.'.join(usernames))

    comparison = None
    if game.lower() in ['bedwars', 'bw']:
        comparison = str(stat_classes.get_stats(usernames, game_mode=game_mode))
    elif game.lower() in ['skywars', 'sw']:
        comparison = str(hypixel.Skywars(usernames, apikey=api_key, game_mode=game_mode))
    elif  game.lower() == 'pit':
        comparison = str(hypixel.Pit(usernames, apikey=api_key, game_mode=game_mode))

    final_msg  = '```\n{0}\n```'.format(comparison if game.lower() in games and comparison else game_string)
    await message.channel.send(final_msg)
    #if game.lower() == 'bedwars':
    #    await message.channel.send(embed=discord.Embed(title='Chamosbot Online', url=stats_page, description='Check out their stats over time!'))
    log('Successfully served {1} stat comparison for {0}'.format(', '.join(usernames), game))


async def send_message_to_channel(message, bot):
    if str(message.author.id) != '580157651548241940':
        await message.author.send('You can\'t use that command')
    else:
        parameters = message.content.split()
        channel_id = parameters[1]
        text = ' '.join(parameters[2:])

        url = 'https://discordapp.com/api/channels/{0}/messages'.format(channel_id)
        headers = {'Authorization': 'Bot {0}'.format(discord_secret)}
        payload = {'content': text}
        req = requests.post(url, headers=headers, data=payload)
        parsed = req.json()


async def get_connected_servers(message, bot):
    user = message.author
    uid = str(user.id)
    current_data = json.loads(open('credentials.json').read())
    hits = []
    for server, keys in current_data['hypixel-api-keys'].items():
        gname, gid = get_guild(server, fields=['name', 'id'])
        if uid in [x[1] for x in keys]:
            hits.append((gname, gid))
    if hits == []:
        await user.send('It looks like your api key isn\'t connected to any servers.')
    else:
        server_list = '\n'.join([x[0] + ' (server ID = ' + x[1] + ')' for x in hits])
        await user.send('Your API key is linked with each of the following servers:\n`{0}`'.format(server_list))


async def remove_hypixel_api_key(message, bot):
    command_format = '`!revokekey <SERVER ID>` or `!revokekey` if you are running the command from the server you want to remove your key from'
    args = message.content.split()[1:]
    guild = message.guild
    user = message.author
    if len(args) == 0 and guild is None:
        await user.send('Sorry, I can\'t tell which server you want me to remove your key from. To see which servers you have a key in, run `!listkeys`, then try the following command again {0}'.format(command_format))
    else:
        gid = args[0] if guild is None else str(guild.id)
        gname = get_guild(gid, fields=['name'])[0]
        uid = str(user.id)
        current_data = json.loads(open('credentials.json').read())
        if uid not in map(lambda x: x[1], current_data['hypixel-api-keys'][gid]):
            # User does not have a key in that server
            await user.send('It looks like you don\'t have a key connected to that server. To see which servers you do have a key in, run `!listkeys`')
        else:
            for key in current_data['hypixel-api-keys'].keys():
                current_data['hypixel-api-keys'][key] = [x for x in current_data['hypixel-api-keys'][key] if x[1] != uid]

            with open('credentials.json', 'w') as _file:
                _file.write(json.dumps(current_data))

            await user.send('Your API key has been removed from {0}.'.format(gname))


async def register_hypixel_api_key(message, bot):
    command_format = '`!addkey <SERVER ID> <HYPIXEL API KEY>`'
    guild = message.guild
    user  = message.author
    args  = message.content.split()[1:]
    if args == []:
        # User only sent !apikey, so DM them asking for more
        await user.send('Thanks for connecting your server to ChamosBot! Please reply to this direct message with the following command: {0} For help finding these, check out {1}/commands/apikey'.format(command_format, website_link))
        if guild is not None: await user.send('btw... it looks like your server ID is {0}, and you should know that your API key will NOT be used by ChamosBot or anyobdy else for anything except providing access to the ChamosBot on your discord server.'.format(guild.id))
    elif len(args) == 2:
        # User sent both parameters, test and save API key
        if guild is not None:
            await user.send('I\'m processing your key, but consider deleting your message from the public guild chat, as the key should be kept private.')

        guild_id, key = args
        await user.send('Your command formatting looks perfect! I\'m testing the API key right now.')
        req = requests.get('https://api.hypixel.net/player?key={0}&name=parcerx'.format(key))
        res = req.json()
        if res['success'] is True:
            # Key works. Save it.
            await user.send('Your key is working! I\'m linking your guild to the key, and I will notify you when the registration is complete.')

            # Save key and user id as tuple
            userkey = (key, str(user.id))

            current_data = json.loads(open('credentials.json').read())
            # If the guild already has a key, add the key to the list
            try:
                current_data['hypixel-api-keys'][guild_id].append(userkey)
            except KeyError as err:
                # If the guild does not have a key, a keyerror will be raised, and
                #   this exception handler just creates a new list of keys for the guild
                current_data['hypixel-api-keys'][guild_id] = [userkey]

            with open('credentials.json', 'w') as credentials_file:
                credentials_file.write(json.dumps(current_data, indent=4, sort_keys=True))

            await user.send('The key is connected! Try running `!stats bedwars gamerboy80` in a text channel that ChamosBot is in!')
        elif res['success'] is False and res['cause'] == 'Invalid API key':
            await user.send('It looks like the API key you provided was incorrect. Please check the key and try the command again.')
        else:
            await user.send('It looks like something may have gone wrong on Hypixel\'s servers when testing your key. Please try again, and be sure to check the key.')
    else:
       await user.send('It seems like the command you sent didn\'t have the right parameters. Please make sure your command follows the format: {0}'.format(command_format))
       await user.send('For help, please visit {0}'.format(website_link))


if __name__ == '__main__':
    print(get_guild('601986871765237761', fields=['name', 'region']))
