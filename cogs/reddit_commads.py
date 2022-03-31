from code import interact
import time
import random
from click import option

import discord
from discord.ext import commands
from discord import Embed

from discord_components import Button, ButtonStyle, Select, SelectOption

from database import Users

from api.reddit_api import get_pic_posts, get_user

class Reddit(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._users = Users()

    async def remove_warning(self, interaction):
        #removing the "interaction failed message"
        try:
            await interaction.respond()
        except:
            pass

    @commands.command(aliases=['fav'])
    async def favourite(self, ctx):
        msg = ctx.message
        is_nsfw = ctx.channel.is_nsfw()

        
        favourites = []

        global fav_index
        fav_index = 0

        async def make_compontents():
            options = []
            index = 0

            favourites = self._users.find({'id':msg.author.id})['favourite']

            for fav in favourites[:25]:
                if (not is_nsfw and not fav['is_nsfw']) or (is_nsfw and fav['is_nsfw']):
                    index += 1
                    options.append(SelectOption(label=str(index) + '. ' + fav['title'][:97], value=str(index-1)))
                else:
                    favourites.remove(fav)

            if options:
                async def callback(interaction):
                    global fav_index
                    fav_index = int(interaction.values[0])
                    await interaction.message.edit(content=favourites[fav_index]['url'])
                    await self.remove_warning(interaction)
                    
                buttons = [
                        Button(custom_id='up',
                            emoji='🔺',
                            style=ButtonStyle.grey),
                        Button(custom_id='down',
                            emoji='🔻',
                            style=ButtonStyle.grey),
                        Button(custom_id='remove',
                            emoji='❌',
                            style=ButtonStyle.grey),
                        Button(custom_id='remove_fav',
                            emoji='🗑',
                            style=ButtonStyle.grey)
                ]

                return [buttons, self._client.components_manager.add_callback(Select(options=options,
                                                                                placeholder=options[0].label),
                                                                        callback)], favourites
            return [], []

        components, favourites = await make_compontents()

        if len(favourites) == 0:
            await msg.reply('You have no favourites')
            return

        message = await ctx.send(favourites[0]['url'], components=components)

        def check(i):
            return i.author == ctx.author and i.message == message

        while True:
            interaction = await self._client.wait_for('button_click', check = check)
            i_id = interaction.custom_id
            if i_id == 'up':
                if fav_index < len(favourites) - 1:
                    fav_index += 1
                    await interaction.message.edit(content=favourites[fav_index]['url'])
            elif i_id == 'down':
                if fav_index > 0:
                    fav_index -= 1
                    await interaction.message.edit(content=favourites[fav_index]['url'])
            elif i_id == 'remove':
                await message.delete()
            elif i_id == 'remove_fav':
                await self.remove_fav(ctx, fav_index)
                fav_index = 0
                components, favourites = await make_compontents()

                if len(favourites) == 0:
                    await message.delete()
                    await msg.reply('You have no favourites')
                    return


                await interaction.message.edit(content=favourites[fav_index]['url'], components=components)

            await self.remove_warning(interaction)
            
    @commands.command(aliases=['rf'])
    async def remove_fav(self, ctx, index=None):
        msg = ctx.message
        if index != None:
            favourites = self._users.find({'id':msg.author.id})['favourite']
            favourites.pop(index)
            self._users.update(msg.author.id, 'favourite', favourites)
        else:
            self._users.update(msg.author.id, 'favourite', [])
            await msg.reply('All you favourites have been deleted')

    @commands.command(aliases=['r'])
    async def reddit(self, ctx, sub):
        msg = ctx.message
        channel_name = ctx.channel.name[1:]
        is_nsfw = ctx.channel.is_nsfw()

        filters = ['.jpg', '.png', '.gif']

        message = None
        #embed = None
        post = None

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

        if posts:
            post = posts[random.randint(0, len(posts)-1)]
            posts.remove(post)

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
                    Button(custom_id='remove',
                        emoji='❌',
                        style=ButtonStyle.grey)
            ]]

            if not post:
                if is_nsfw:
                    message = await msg.reply('Only NFSW content can be showed here', components=[[components[0][0], components[0][3]]])
                else:
                    message = await msg.reply('NFSW content can only be showed in a NSFW chanel', components=[[components[0][0], components[0][3]]])
            else:
                message = await msg.reply(post['url'], components=components)

            def check(i):
                return i.author == ctx.author and i.message == message

            while True:
                interaction = await self._client.wait_for('button_click', check = check)
                i_id = interaction.custom_id
                if i_id == 'up':
                    if len(posts) == 0:
                        posts = get_pic_posts(sub, order_by, is_nsfw)

                    edit_post = posts[random.randint(0, len(posts)-1)]

                    if not edit_post:
                        if is_nsfw:
                            await interaction.message.edit('Only NFSW content can be showed here', components=[[components[0][0], components[0][3]]])
                        else:
                            await interaction.message.edit('NFSW content can only be showed in a NSFW chanel', components=[[components[0][0], components[0][3]]])
                        await self.remove_warning(interaction)
                    else:
                        post = edit_post
                        await interaction.message.edit(content=edit_post['url'], components=components)
                        posts.remove(edit_post)
                elif i_id == 'info':
                    embed = Embed(title=post['title'], description=f"This post is from the {post['subreddit_name_prefixed']} subreddit", color=0x2d8bfc)
                    await interaction.respond(embed=embed)
                elif i_id == 'fav':
                    embed = Embed(title=post['title'], description=f"This post is from the {post['subreddit_name_prefixed']} subreddit", color=0x2d8bfc)
                    fav_data = {'title':embed.title,
                                'description':embed.description,
                                'url':post['url'],
                                'is_nsfw': is_nsfw}
                    self._users.insert_to_list(interaction.author.id, 'favourite', fav_data)
                    
                    response_emb = Embed(title='You have saved this post', description=embed.title+'\n'+embed.description)
                    await interaction.respond(embed=response_emb)
                elif interaction.custom_id == 'remove':
                    await message.delete()

                await self.remove_warning(interaction)

    @commands.command(aliases=['u'])
    async def user(self, ctx, name):
        msg = ctx.message

        user_info = get_user(name)

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

def setup(client):
    client.add_cog(Reddit(client))









































#Code dump
'''
    @commands.command(aliases=['of'])#aliases=['fav', 'Fav', 'favs', 'Favs', 'favourites', 'Favourites', 'Favourite'])
    async def old_favourite(self, ctx, index = None):
        msg = ctx.message
        is_nsfw = ctx.channel.is_nsfw()
        favourites = self._users.find({'id':msg.author.id})['favourite']

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
            await msg.reply(embed=embed)
            await ctx.send(fav_info['url'])
        else:
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
                await msg.reply(embed=embed)
                await ctx.send(fav_info['url'])
'''