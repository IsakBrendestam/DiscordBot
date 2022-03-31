import time

import discord
from discord.ext import commands

from database import Users

class Events(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._users = Users()
    
    @commands.Cog.listener()
    async def on_ready(self):
        ''' Bot is starting '''

        await self._client.change_presence(status=discord.Status.online,
                                            activity=discord.Game('Lisening to ![commad]'))

        # #setting channel to write in
        # chanel_id = get_chanel_id('general')
        # channel = client.get_channel(chanel_id)

        # #sending message that can be reacted on
        # text = 'React here!'
        # message = await channel.send(text)
        # emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

        # #adding reactions to message
        # for emoji in emojis:
        #     await message.add_reaction(emoji=emoji)

        #bot is ready to start being used
        t = time.localtime()
        current_time = time.strftime("%D - %H:%M:%S", t)
        print('We have logged in as {0.user} at {1}'.format(self._client, current_time))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ''' Member joined the server '''

        data = {
            'name': member.name,
            'display_name': member.display_name,
            'id': member.id,
            'nick': member.nick,
            'joined_at': member.joined_at,
            'favourite': None
            }

        self._users.insert(data)

        await member.send('welcome to the server')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self._users.delete_all('id', member.id)

def setup(client):
    client.add_cog(Events(client))
