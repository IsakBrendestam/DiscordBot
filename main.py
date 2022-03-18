import discord
from discord.ext import commands

import time
import random

import nasa_api
from reddit_api import get_pic_posts, get_user
from utils import load_config

client = commands.Bot(command_prefix=('!'))

def get_chanel_id(name):
    chanel = discord.utils.get(client.get_all_channels(), name=name)
    if not chanel:
        return None
    return chanel.id


# Events

@client.event
async def on_ready():
    ''' Bot is starting '''

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
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = client.get_user(payload.user_id)

@client.event
async def on_reaction_add(reaction, user):
    ''' Reaction on message '''
    if user == client.user:
        #the bot reacted
        return
   
    #checking for reactions in general
    chanel_id = get_chanel_id('general')
    channel = client.get_channel(chanel_id)

    reaction_role = {'1️⃣':'Test 1', '2️⃣':'Test 2', '3️⃣':'Test 3', '4️⃣':'Test 4', '5️⃣':'Test 5', '6️⃣':'Test 6', '7️⃣':'Test 7', '8️⃣':'Test 8', '9️⃣':'Test 9'}

    if reaction.message.channel == channel:
        #reacted in general
        if reaction.message.author == client.user:
            #reacted on bots message
            if reaction.emoji in reaction_role.keys():
                #adding role to user
                role = discord.utils.get(user.guild.roles, name=reaction_role[reaction.emoji])

                if not role:
                    return

                await user.add_roles(role)

client.event
async def on_member_join(member):
    ''' Member joined the server '''
    await member.send('welcome to the server')


# Commands

@client.command(aliases=['Nasa'])
async def nasa(ctx):
    #creates embed
    embed = discord.Embed(title='This is the daily picture from NASA', description="Every day nasa publishes a picture from space, and this is the one from today", color=0x2d8bfc)
    embed.set_image(url=nasa_api.get_nasa_picture())

    #Sending the nasa picture in a embed
    await ctx.send(embed=embed)

@client.command(aliases=['r'])
async def reddit(ctx, sub, amount=1):
    last_message = ctx.channel.last_message
    channel_name = ctx.channel.name[1:]
    is_nsfw = ctx.channel.is_nsfw()

    filters = ['.jpg', '.png', '.gif']

    limit = 100

    server_order = {'hot':f'hot?limit={limit}', 
                    'new':f'new?limit={limit}', 
                    'rising':f'rising?limit={limit}',
                    'top-now':f'top?limit={limit}&t=hour',
                    'top-this-month':f'top?limit={limit}&t=month',
                    'top-this-year':f'top?limit={limit}&t=year',
                    'top-all-time':f'top?limit={limit}&t=all'}

    order_by = 'top/?t=all'
    if channel_name in server_order.keys():
        order_by = server_order[channel_name]

    posts = get_pic_posts(sub, order_by, is_nsfw)
    
    if not posts:
        await last_message.reply('There is no data from this subreddit')
        return

    if len(posts) == 0:
        await last_message.reply('There is no images or GIFs from this subreddit')
        return

    for _ in range(amount):
        if posts:
            post = posts[random.randint(0, len(posts)-1)]
            posts.remove(post)

            if not post:
                if is_nsfw:
                    await last_message.reply('Only NFSW content can be showed here')
                else:
                    await last_message.reply('NFSW content can only be showed in a NSFW chanel')
                return

            if any(file_type == post['url'][-len(file_type):] for file_type in filters):
                embed = discord.Embed(title=post['title'], description=f"This is a picture from {post['subreddit_name_prefixed']}", color=0x2d8bfc)
                embed.set_image(url=post['url'])
                await last_message.reply(embed=embed)
            else:
                embed = discord.Embed(title=post['title'], description=f"This is a GIF from {post['subreddit_name_prefixed']}", color=0x2d8bfc)
                await last_message.reply(embed=embed)
                await ctx.send(post['url'])
            
            time.sleep(0.1)

@client.command(aliases=['u'])
async def user(ctx, name):
    last_message = ctx.channel.last_message

    user_info = get_user(name)
    #print(json.dumps(user_info, indent=4, sort_keys=True))

    if 'error' in user_info.keys():
        await last_message.reply(f'An error uccured: {user_info["message"]}')
        return

    user_info = user_info['data']

    karma = user_info['total_karma']
    sub_data = user_info['subreddit']

    title = sub_data['display_name_prefixed']

    description = f'Karma\n 💮: {karma}'

    embed = discord.Embed(title=title, description=description)
    embed.set_thumbnail(url=user_info['snoovatar_img'])

    await last_message.reply(embed=embed)

@client.command()
async def clear(ctx, amount=None):
    if amount:
        amount = int(amount)

    await ctx.channel.purge(limit=amount,  check=lambda msg: not msg.pinned)


if __name__ == '__main__':
    #Loading the
    config = load_config('../bot_config.yml')
    client.run(config['token'])