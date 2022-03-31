from discord.ext import commands

class ServerCommands(commands.Cog):
    def __init__(self, client):
        self._client = client

    def can_clear(self, ctx):
        return any(role.name=='Moderators' for role in ctx.author.roles)

    @commands.check(can_clear)
    @commands.command()
    async def clear(ctx, amount=None):
        if amount:
            if amount.isnumeric():
                amount = int(amount)
            else:
                return

        await ctx.channel.purge(limit=amount,  check=lambda msg: not msg.pinned)

def setup(client):
    client.add_cog(ServerCommands(client))