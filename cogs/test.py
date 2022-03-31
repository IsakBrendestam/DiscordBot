from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, client):
        self._client = client
        
    @commands.command()
    async def test(self, ctx):
        print('test')


def setup(client):
    client.add_cog(Test(client))
