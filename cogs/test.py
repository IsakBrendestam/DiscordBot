from discord.ext import commands
from discord_components import Button, ButtonStyle

class Test(commands.Cog):
    def __init__(self, client):
        self._client = client
        
    @commands.command()
    async def test(self, ctx):
        print('test')

    @commands.command()
    async def btn(self, ctx):
        components = components = [[
                        Button(custom_id='n1',
                            label='\a',
                            style=ButtonStyle.grey,
                            disabled=True),
                        Button(custom_id='1',
                            emoji='⬆️',
                            style=ButtonStyle.grey),
                        Button(custom_id='n2',
                            label='\a',
                            style=ButtonStyle.grey,
                            disabled=True)],
                    [
                        Button(custom_id='2',
                            emoji='⬅️',
                            style=ButtonStyle.grey),
                        Button(custom_id='n3',
                            emoji='🖲',
                            style=ButtonStyle.grey),
                        Button(custom_id='3',
                            emoji='➡️',
                            style=ButtonStyle.grey)],
                    [
                        Button(custom_id='n4',
                            label='\a',
                            style=ButtonStyle.grey,
                            disabled=True),
                        Button(custom_id='4',
                            emoji='⬇️',
                            style=ButtonStyle.grey),
                        Button(custom_id='n5',
                            label='\a',
                            style=ButtonStyle.grey,
                            disabled=True)]]

        await ctx.send(components=components)

def setup(client):
    client.add_cog(Test(client))


# a = '''
# \a\a\a\a\a\a\a\aa\a\a\a\ab\a\a\a\a\ac\a\a\a\ad\a\a\a\a\ae\a\a\a\af\a\a\a\a\ag\a\a\a\ah\a\a\a\a\ai\a\a\a\a\aj\a\a\a\a\ak\a\a\a\a\al\a\a\a\am\a\a\a\an

# 1 \a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 2\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 3\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 4\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 5\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 6\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 7\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 8\a\a\a\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦\a\a🟦

# 9\a\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 10\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 11 \a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 12\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 13\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦

# 14\a\a\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦\a 🟦 \a 🟦 \a 🟦 \a 🟦 \a 🟦
# '''


# print(a.split('\n'))