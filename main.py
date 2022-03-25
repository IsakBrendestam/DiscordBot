import time
import random
import sys
import traceback

#discord libraries
import discord
from discord.ext import commands, tasks
from discord import Button, ButtonStyle, Embed

#api libraries
import nasa_api
from reddit_api import get_pic_posts, get_user

from utils import load_config

from database import Users

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=('!'),
                      intents=intents)

#user database
users = Users()

def get_chanel_id(name):
    chanel = discord.utils.get(client.get_all_channels(), name=name)
    if not chanel:
        return None
    return chanel.id


# Events

@client.event
async def on_ready():
    ''' Bot is starting '''

    await client.change_presence(status=discord.Status.online,
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
    print('We have logged in as {0.user} at {1}'.format(client, current_time))

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

@client.event
async def on_member_join(member):
    ''' Member joined the server '''

    data = {
        'name': member.name,
        'display_name': member.display_name,
        'id': member.id,
        'nick': member.nick,
        'joined_at': member.joined_at,
        'favourite': None
        }

    users.insert(data)

    await member.send('welcome to the server')

@client.event
async def on_member_remove(member):
    users.delete_all('id', member.id)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        pass
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Commands

@client.command(aliases=['Nasa'])
async def nasa(ctx):
    #creates embed
    embed = discord.Embed(title='This is the daily picture from NASA', description="Every day nasa publishes a picture from space, and this is the one from today", color=0x2d8bfc)
    embed.set_image(url=nasa_api.get_nasa_picture())

    #Sending the nasa picture in a embed
    await ctx.send(embed=embed)

@client.command(aliases=['rf'])
async def remove_fav(ctx, index=None):
    msg = ctx.message

    if not index:
        users.update(msg.author.id, 'favourite', [])
        await msg.reply('All you favourites have been deleted')

@client.command(aliases=['fav', 'Fav', 'favs', 'Favs', 'favourites', 'Favourites', 'Favourite'])
async def favourite(ctx, index = None):
    msg = ctx.message
    is_nsfw = ctx.channel.is_nsfw()
    favourites = users.find({'id':msg.author.id})['favourite']

    if not favourites:
        await msg.reply('You have no favourite posts')

    if index:
        if not index.isnumeric():
            await msg.reply('index must be a number')
            return

        i = int(index)

        # if index is to low
        if i < 1: i = 1

        # if index is to high
        if i > len(favourites): i = len(favourites)

        fav_info = favourites[i-1]
        if is_nsfw and not fav_info['is_nsfw']:
            #SFW content is beeing sent in NSFW channel
            await msg.reply('Only NFSW content can be showed here')
            return

        if not is_nsfw and fav_info['is_nsfw']:
            #NSFW content is beeing sent in SFW channel
            await msg.reply('NFSW content can only be showed in a NSFW chanel')
            return

        embed = Embed(title=fav_info['title'], description=fav_info['description'], color=0x2d8bfc)
        embed.set_image(url=fav_info['url'])
        await msg.reply(embed=embed)
        return

    for fav_info in favourites:
        if is_nsfw and not fav_info['is_nsfw']:
            #SFW content is beeing sent in NSFW channel
            await msg.reply('Only NFSW content can be showed here')
            continue

        if not is_nsfw and fav_info['is_nsfw']:
            #NSFW content is beeing sent in SFW channel
            await msg.reply('NFSW content can only be showed in a NSFW chanel')
            continue

        embed = Embed(title=fav_info['title'], description=fav_info['description'], color=0x2d8bfc)
        embed.set_image(url=fav_info['url'])
        await msg.reply(embed=embed)

@client.command(aliases=['r'])
async def reddit(ctx, sub, amount=1):
    msg = ctx.message
    channel_name = ctx.channel.name[1:]
    is_nsfw = ctx.channel.is_nsfw()

    filters = ['.jpg', '.png', '.gif']

    limit = 100

    #diffrent ways to order reddit
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

    #getting post from reddit
    posts = get_pic_posts(sub, order_by, is_nsfw)
    
    #checking if any posts where found
    if not posts:
        await msg.reply('There is no data from this subreddit')
        return

    if len(posts) == 0:
        await msg.reply('There is no images or GIFs from this subreddit')
        return

    components = [[
        Button(custom_id='up',
               emoji='🔺',
               style=ButtonStyle.grey),
        Button(custom_id='info',
               emoji='❓',
               style=ButtonStyle.grey),
        Button(custom_id='fav',
               emoji='🌟',
               style=ButtonStyle.grey),
        Button(custom_id='down',
               emoji='❌',
               style=ButtonStyle.grey),
    ]]

    message = None
    embed = None

    for _ in range(amount):
        if posts:
            post = posts[random.randint(0, len(posts)-1)]
            posts.remove(post)

            if not post:
                if is_nsfw:
                    await msg.reply('Only NFSW content can be showed here', components=components[:2])
                else:
                    await msg.reply('NFSW content can only be showed in a NSFW chanel', components=components[:2])
                return

            embed = Embed(title=post['title'], description=f"This post is from the {post['subreddit_name_prefixed']} subreddit", color=0x2d8bfc)
            message = await msg.reply(post['url'], components=components)
            time.sleep(0.1)

    saved = False

    #waiting for reaction on button
    while True:
        def check_button(i: discord.Interaction, button):
            return i.author == ctx.author and i.message == message

        interaction, button = await client.wait_for('button_click', check=check_button)
        if button.custom_id == 'up':
            await interaction.message.delete()
            await reddit(ctx, sub, 1)
        elif button.custom_id == 'down':
            await message.delete()
        elif button.custom_id == 'info':
            await interaction.respond(embed=embed, hidden=True)
        elif button.custom_id == 'fav' and not saved:
            fav_data = {'title':embed.title,
                        'description':embed.description,
                        'url':post['url'],
                        'is_nsfw': is_nsfw}
            users.insert_to_list(interaction.author.id, 'favourite', fav_data)
            
            response_emb = Embed(title='You have saved this post', description=embed.title+'\n'+embed.description)
            saved = True
            await interaction.respond(embed=response_emb, hidden=True)
        elif button.custom_id == 'fav' and saved:
            await interaction.respond('You alredy saved this post', hidden=True)

@client.command(aliases=['u'])
async def user(ctx, name):
    msg = ctx.message

    user_info = get_user(name)
    #print(json.dumps(user_info, indent=4, sort_keys=True))

    if 'error' in user_info.keys():
        await msg.reply(f'An error uccured: {user_info["message"]}')
        return

    user_info = user_info['data']

    karma = user_info['total_karma']
    sub_data = user_info['subreddit']

    title = sub_data['display_name_prefixed']

    description = f'Karma\n 💮: {karma}'

    embed = discord.Embed(title=title, description=description)
    embed.set_thumbnail(url=user_info['snoovatar_img'])

    await msg.reply(embed=embed)

def can_clear(ctx):
    return any(role.name=='Moderators' for role in ctx.author.roles)

@client.command()
@commands.check(can_clear)
async def clear(ctx, amount=None):
    if amount:
        if amount.isnumeric():
            amount = int(amount)
        else:
            return

    await ctx.channel.purge(limit=amount,  check=lambda msg: not msg.pinned)

if __name__ == '__main__':
    #Loading the token
    config = load_config('../configs/bot_config.yml')
    client.run(config['token'])


#The code dump
'''
#post can be sent in embed
if any(file_type == post['url'][-len(file_type):] for file_type in filters):



@tasks.loop(seconds=10)
async def something():
    #updates every 10 seconds
    pass

#check for rolse settings
@commands.has_permissions(manage_messages=True)
'''
