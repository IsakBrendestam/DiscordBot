import discord
from discord.ext import commands

from api.nasa_api import get_nasa_picture

class Nasa(commands.Cog):
    def __init__(self, client):
        self._client = client

    @commands.command(name='nasa', description='haha')
    async def nasa(self, ctx):
        #creates embed
        print('test')
        embed = discord.Embed(title='This is the daily picture from NASA', description="Every day nasa publishes a picture from space, and this is the one from today", color=0x2d8bfc)
        embed.set_image(url=get_nasa_picture())

        #Sending the nasa picture in a embed
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Nasa(client))
