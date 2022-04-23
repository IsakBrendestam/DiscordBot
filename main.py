import os

import discord

from discord_components import ComponentsBot

from utils import load_config


import ctypes
import ctypes.util

# if not discord.opus.is_loaded():
#     print("ctypes - Find opus:")
#     a = ctypes.util.find_library('opus')
#     print(a)
    
#     print("Discord - Load Opus:")
#     b = discord.opus.load_opus(a)
#     print(b)
    
#     print("Discord - Is loaded:")
#     c = discord.opus.is_loaded()
#     print(c)

intents = discord.Intents().all()
intents.members = True

client = ComponentsBot(command_prefix='!',
                      intents=intents)


if __name__ == '__main__':
    files = os.listdir('cogs/')
    for filename in files:
        if filename.endswith(".py"):
            client.load_extension('cogs.{0}'.format(filename[:-3]))

    # discord.opus.load_opus('opus')
    config = load_config('../configs/bot_config.yml')
    client.run(config['token'])

































#The code dump
'''
#post can be sent in embed
if any(file_type == post['url'][-len(file_type):] for file_type in filters):

----------------------------------------------------------------------------------------------------

@tasks.loop(seconds=10)
async def something():
    #updates every 10 seconds
    pass

----------------------------------------------------------------------------------------------------

#check for rolse settings
@commands.has_permissions(manage_messages=True)

----------------------------------------------------------------------------------------------------

#bot class
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        # client = commands.Bot(command_prefix=('!'),
        #                         intents=intents)
        
        super().__init__(
            command_prefix='!',
            intents = intents
        )

    async def setup_hook(self):
        files = os.listdir('cogs/')
        for filename in files:
            if filename.endswith(".py"):
                await self.load_extension('cogs.{0}'.format(filename[:-3]))

    
    async def close(self):
        await super().close()

# async def main(self):
#     config = load_config('../configs/bot_config.yml')

#     async with client:
#         await load_extensions()
#         await client.start(config['token'])

if __name__ == '__main__':
    #client.run(config['token'])
    client = Bot()
    config = load_config('../configs/bot_config.yml')
    client.run(config['token'])
    #asyncio.run(main())

----------------------------------------------------------------------------------------------------


'''
