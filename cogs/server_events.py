import time

import discord
from discord.ext import commands

from database import Servers

from pprint import pprint

class Events(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._server = Servers()

    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):
        if not any(guild.id == s['server_id'] for s in self._server.get_all_elements()):
            server_indfo = {
                'server_id': guild.id,
                'server_name': guild.name,
                'server_owner': guild.owner.name,
                'server_owner_id': guild.owner_id,
                'server_creation_date': guild.created_at,
                'users': []
            }

            for member in guild.members:
                if not member.bot:
                    member_data = {
                        'name': member.name,
                        'display_name': member.display_name,
                        'id': member.id,
                        'nick': member.nick,
                        'joined_at': member.joined_at,
                        'favourite': None
                    }

                    server_indfo['users'].append(member_data)

            self._server.insert(server_indfo)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild:discord.Guild):
        self._server.delete_one('server_id', guild.id)

    @commands.Cog.listener()
    async def on_ready(self):
        ''' Bot is starting '''

        await self._client.change_presence(status=discord.Status.online,
                                            activity=discord.Game('Lisening to ![commad]'))

        #bot is ready to start being used
        t = time.localtime()
        current_time = time.strftime("%D - %H:%M:%S", t)
        print('We have logged in as {0.user} at {1}'.format(self._client, current_time))

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        ''' Member joined the server '''

        user_data = {
            'name': member.name,
            'display_name': member.display_name,
            'id': member.id,
            'nick': member.nick,
            'joined_at': member.joined_at,
            'favourite': None
            }

        self._server.insert_to_list('server_id', member.guild.id, 'users', user_data)

        await member.send('welcome to the server')

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        user_data = self._server.find({'server_id': member.guild.id})['users']

        for i, user in enumerate(user_data):
            if user['id'] == member.id:
                user_data.pop(i)

        pprint(user_data)
        self._server.update('server_id', member.guild.id, 'users', user_data)

def setup(client):
    client.add_cog(Events(client))















































'''
    @commands.command()
    async def add(self, ctx:commands.context.Context):
        guild = ctx.guild


        server_indfo = {
            'server_id': guild.id,
            'server_name': guild.name,
            'server_owner': guild.owner.name,
            'server_owner_id': guild.owner_id,
            'server_creation_date': guild.created_at,
            'users': []
        }

        for i in self._users.get_first(2):
            server_indfo['users'].append(i)


        self._server.insert(server_indfo)

    @commands.command()
    async def add(self, ctx:commands.context.Context):
        guild = ctx.guild
        server_indfo = {
                'server_id': guild.id,
                'server_name': guild.name,
                'server_owner': guild.owner.name,
                'server_owner_id': guild.owner_id,
                'server_creation_date': guild.created_at,
                'users': []
            }

            for member in guild.members:
                if not member.bot:
                    member_data = {
                        'name': member.name,
                        'display_name': member.display_name,
                        'id': member.id,
                        'nick': member.nick,
                        'joined_at': member.joined_at,
                        'favourite': None
                    }

                    server_indfo['users'].append(member_data)

            self._server.insert(server_indfo)

    
    @commands.command()
    async def add(self, ctx:commands.context.Context):
        guild = ctx.guild
        server_indfo = {
                'server_id': guild.id,
                'server_name': guild.name,
                'server_owner': guild.owner.name,
                'server_owner_id': guild.owner_id,
                'server_creation_date': guild.created_at,
                'users': []
            }

        for member in guild.members:
            if not member.bot:
                member_data = {
                    'name': member.name,
                    'display_name': member.display_name,
                    'id': member.id,
                    'nick': member.nick,
                    'joined_at': member.joined_at,
                    'favourite': [fav for fav in self._users.find({'id':member.id})['favourite']]
                }

                server_indfo['users'].append(member_data)

        self._server.insert(server_indfo)
'''