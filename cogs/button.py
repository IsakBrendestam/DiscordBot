
from discord.ext import commands

from discord_components import Button

class MyButton(commands.Cog):
    def __init__(self, client):
        self._client = client

    @commands.command()
    async def button(self, ctx):
        await ctx.send(
            "Hello, World!",
            components = [
                            Button(label = "WOW button!", custom_id = "button1")
                        ],
        )

def setup(client):
    client.add_cog(MyButton(client))