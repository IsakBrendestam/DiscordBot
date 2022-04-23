from discord.ext import commands

class ServerCommands(commands.Cog):
    def __init__(self, client):
        self._client = client

    async def can_clear(ctx):
        return any(role.name=='Moderators' for role in ctx.author.roles)

    @commands.command()
    @commands.check(can_clear)
    async def clear(self, ctx, amount=None):
        if amount != None:
            if amount.isnumeric():
                amount = int(amount)
            else:
                return

        await ctx.channel.purge(limit=amount,  check=lambda msg: not msg.pinned)

        

def setup(client):
    client.add_cog(ServerCommands(client))