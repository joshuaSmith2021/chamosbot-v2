#!/usr/bin/python3

import datetime
import json

import discord
import tools
from tools import log
import hypixel


def log(text):
    print('{0}: {1}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text))


class ChamosBot(discord.Client):
    async def on_ready(self):
        log('Logged in as {0}, id {1}'.format(self.user.name, self.user.id))

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!stats'):
            await tools.get_game_stats(message, self)

        elif message.content.startswith('!link'):
            parameters = message.content.split()[1:]
            usernames = parameters
            stats_page = 'http://chamosbotonline.herokuapp.com/bedwars?igns={0}'.format('.'.join(usernames))
            await message.channel.send(embed=discord.Embed(title='Chamosbot Online', url=stats_page, description='Check out their stats over time!'))

        elif message.content.startswith('!addkey'):
            await tools.register_hypixel_api_key(message, self)

        elif message.content.startswith('!revokekey'):
            await tools.remove_hypixel_api_key(message, self)

        elif message.content.startswith('!listkeys'):
            # Show the user which servers their key is in
            await tools.get_connected_servers(message, self)

        elif message.content.startswith('!help'):
            await tools.send_help_message(message, self)

        elif message.content.startswith('!sendto'):
            await tools.send_message_to_channel(message, self)


    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)


discord_secret = json.loads(open('credentials.json').read())['discord-token'] 

client = ChamosBot()
client.run(discord_secret)
