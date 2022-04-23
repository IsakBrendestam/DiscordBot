import random

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
        ''' Removes the warning from a interaction
                :Parameters:
                    interaction: the interaction that the user interacted with
        '''
        try:
            await interaction.respond()
        except:
            pass

    @commands.command(aliases=['fav'])
    async def favourites(self, ctx):
        '''  Displays the users favourite posts and handles buttons and selection
             that the user can use to manage their favouries
                :paraneters:
                    ctx: 
        '''

        msg = ctx.message
        is_nsfw = ctx.channel.is_nsfw()

        favourites = []

        global fav_index
        fav_index = 0

        global db_fav_index
        db_fav_index = {}

        async def make_compontents():
            ''' Creates the components that will be used in the message '''

            options = []
            index = 0
            
            temp_favourites = self._users.find({'id':msg.author.id})['favourite']

            global db_fav_index
            db_fav_index = {}

            favourites = []
            for i, fav in enumerate(temp_favourites):
                if (not is_nsfw and not fav['is_nsfw']) or (is_nsfw and fav['is_nsfw']):
                    #checking if post belongs to the chanel
                    db_fav_index[index] = i
                    index += 1
                    if len(options) < 25:
                        #adding post to the selection
                        options.append(SelectOption(label=str(index) + '. ' + fav['title'][:97], value=str(index-1)))
                    favourites.append(fav)


            if options:
                async def callback(interaction):
                    ''' Handeling what should happen when a selection is made
                            :parameters: 
                                interaction: the interaction element that is made
                                             when a selection is made 
                    '''

                    global fav_index
                    fav_index = int(interaction.values[0])
                    #displays the selected post
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
            # no favourites where found
            return [], []

        components, favourites = await make_compontents()

        if len(favourites) == 0:
            # no favourites where found
            await msg.reply('You have no favourites')
            return

        message = await ctx.send(favourites[0]['url'], components=components)

        def check(i):
            ''' Checking that the right user clicks a button and that is's the right message
                    :parametes:
                        i: potential interaction element
            '''
            return i.author == ctx.author and i.message == message

        while True:
            # waiting for a interaction on any of the buttons

            interaction = await self._client.wait_for('button_click', check = check)
            i_id = interaction.custom_id
            if i_id == 'up':
                # scrolling up in the list
                if fav_index > 0:
                    fav_index -= 1
                    await interaction.message.edit(content=favourites[fav_index]['url'])
            elif i_id == 'down':
                # scrolling down in the list
                if fav_index < len(favourites) - 1:
                    fav_index += 1
                    await interaction.message.edit(content=favourites[fav_index]['url'])
            elif i_id == 'remove':
                # removing the message
                await message.delete()
            elif i_id == 'remove_fav':
                # removing the favourite from the database
                await self.remove_fav(ctx, db_fav_index[fav_index])

                # selecting a new favourite to dusplay
                if fav_index != 0:
                    fav_index -= 1

                components, favourites = await make_compontents()

                if len(favourites) == 0:
                    # the last favourite was removed
                    await message.delete()
                    await msg.reply('You have no favourites')
                    return

                await interaction.message.edit(content=favourites[fav_index]['url'], components=components)

            await self.remove_warning(interaction)
            
    @commands.command(aliases=['rf'])
    async def remove_fav(self, ctx, index=None):
        ''' Removing a favourite from the databse
                :parameters:
                    ctx:
                    index: the index of the favourite that should be removed
                           if None all elements will be removed 
        '''

        msg = ctx.message
        if index != None:
            #removing all favourites
            favourites = self._users.find({'id':msg.author.id})['favourite']
            favourites.pop(index)
            self._users.update('id', msg.author.id, 'favourite', favourites)
        else:
            #removing favorute with specific index
            self._users.update('id', msg.author.id, 'favourite', [])
            await msg.reply('All you favourites have been deleted')

    @commands.command(aliases=['r'])
    async def reddit(self, ctx, sub):
        ''' Gets a random post from a subreddit and then displays it,
            the filter for the subreddit is determined by the name of the chanel,
            also handles the buttons for the message
                :parameters:
                    ctx:
                    sub: the subreddit to get posts from
        '''
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
            #selects the order depending on the channel name
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
            #getting a random post out of all
            post = posts[random.randint(0, len(posts)-1)]
            posts.remove(post)

            #buttons that is to be sent in the message
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
                #post should not be sent
                if is_nsfw:
                    message = await msg.reply('Only NFSW content can be showed here', components=[[components[0][0], components[0][3]]])
                else:
                    message = await msg.reply('NFSW content can only be showed in a NSFW chanel', components=[[components[0][0], components[0][3]]])
            else:
                #sending post
                message = await msg.reply(post['url'], components=components)

            def check(i):
                ''' Checking that the right user clicks a button and that is's the right message
                        :parameters:
                            i: potential interaction element
                '''
                return i.author == ctx.author and i.message == message

            while True:
                #waiting for interaction
                interaction = await self._client.wait_for('button_click', check = check)
                i_id = interaction.custom_id

                if i_id == 'up':
                    #generating new post

                    if len(posts) == 0:
                        #all bosts have been scorlled throu
                        posts = get_pic_posts(sub, order_by, is_nsfw)

                    edit_post = posts[random.randint(0, len(posts)-1)]

                    if not edit_post:
                        #post should not be sent
                        if is_nsfw:
                            await interaction.message.edit('Only NFSW content can be showed here', components=[[components[0][0], components[0][3]]])
                        else:
                            await interaction.message.edit('NFSW content can only be showed in a NSFW chanel', components=[[components[0][0], components[0][3]]])
                        await self.remove_warning(interaction)
                    else:
                        #sending post
                        post = edit_post
                        await interaction.message.edit(content=edit_post['url'], components=components)
                        posts.remove(edit_post)
                elif i_id == 'info':
                    #displaying info about the post
                    embed = Embed(title=post['title'], description=f"This post is from the {post['subreddit_name_prefixed']} subreddit", color=0x2d8bfc)
                    await interaction.respond(embed=embed)
                elif i_id == 'fav':
                    #adding post to favourite
                    user_id = interaction.author.id

                    embed = Embed(title=post['title'], description=f"This post is from the {post['subreddit_name_prefixed']} subreddit", color=0x2d8bfc)
                    
                    fav_data = {'title':embed.title,
                                'description':embed.description,
                                'url':post['url'],
                                'is_nsfw': is_nsfw}

                    #checking if post is in databse
                    if any(post['url'] == sublist['url'] for sublist in self._users.find({'id':user_id})['favourite']):
                        await message.reply('This post is alredy saved')
                    else:
                        #adding post to database
                        self._users.insert_to_list('id', user_id, 'favourite', fav_data)     
                        response_emb = Embed(title='You have saved this post', description=embed.title+'\n'+embed.description)
                        await interaction.respond(embed=response_emb)
                elif interaction.custom_id == 'remove':
                    #removing the post from the chanel
                    await message.delete()

                await self.remove_warning(interaction)

    @commands.command(aliases=['u'])
    async def user(self, ctx, name):
        ''' Getting data form reddit about a specific user
                :parametes:
                    ctx:
                    name: the name of the user
        '''
        msg = ctx.message

        # getting the data from the user using the reddit api
        user_info = get_user(name)

        if 'error' in user_info.keys():
            # user was most likley not found
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