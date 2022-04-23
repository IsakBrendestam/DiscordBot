from pprint import pprint
import discord
from discord.ext import commands
from discord.ext.commands.context import Context as Ctx
from discord import Embed
from discord_components import Button, ButtonStyle

from random import randint

class Player:
    def __init__(self, member:discord.Member, channel:discord.TextChannel):
        self._member = member
        self._channel = channel
        self._embed = None
        self._map = None
        self._board_message = None
        self._boat_positions = None
        self._shots = []
        self._hits = []
        self._life = 0
        self._status = None
        self._components = [[
                             Button(custom_id='up_left',
                                 label='↖️',
                                 style=ButtonStyle.grey),
                             Button(custom_id='up',
                                 emoji='⬆️',
                                 style=ButtonStyle.grey),
                             Button(custom_id='up_right',
                                 label='↗️',
                                 style=ButtonStyle.grey)],
                            [
                             Button(custom_id='left',
                                 emoji='⬅️',
                                 style=ButtonStyle.grey),
                             Button(custom_id='shoot',
                                 label='🖲',
                                 style=ButtonStyle.grey),
                             Button(custom_id='right',
                                 emoji='➡️',
                                 style=ButtonStyle.grey)],
                            [
                             Button(custom_id='down_left',
                                 label='↙️',
                                 style=ButtonStyle.grey),
                             Button(custom_id='down',
                                 emoji='⬇️',
                                 style=ButtonStyle.grey),
                             Button(custom_id='down_right',
                                 label='↘️',
                                 style=ButtonStyle.grey)]]

    @property
    def name(self) -> str:
        return self._member.display_name

    @property
    def member(self) -> discord.Member:
        return self._member

    @property
    def health(self) -> int:
        return self._life

    @property
    def channel(self) -> discord.TextChannel:
        return self._channel

    @property
    def embed(self) -> discord.Embed:
        return self._embed

    @embed.setter
    def embed(self, embed:discord.Embed):
        self._embed = embed

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status:str):
        self._status = status

    @property
    def boat_positions(self) -> list:
        return self._boat_positions

    @boat_positions.setter
    def boat_positions(self, positions:list):
        self._boat_positions = positions
        self.update_life()

    def remove_boat_position(self, position:list):
        self._boat_positions.remove(position)
        self.update_life()

    @property
    def shots(self) -> list:
        return self._shots

    def add_shot(self, shot:tuple):
        self._shots.append(shot)

    @property
    def map(self) -> list:
        return self._map
    
    @map.setter
    def map(self, map:list):
        self._map = map

    @property
    def message(self) -> discord.message:
        return self._board_message

    @message.setter
    def message(self, message:discord.message):
        self._board_message = message

    @property
    def hits(self) -> list:
        return self._hits

    def add_hit(self, pos:tuple):
        self._hits.append(pos)

    @property
    def components(self) -> list:
        return self._components

    def update_life(self):
        self._life = len(self._boat_positions)
        

class Game(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._player1:Player = None
        self._player2:Player = None

    async def remove_warning(self, interaction):
        ''' Removes the warning from a interaction
                :Parameters:
                    interaction: the interaction that the user interacted with
        '''
        try:
            await interaction.respond()
        except:
            pass

    @commands.command(aliases=['bs'])
    async def battleship(self, ctx:Ctx):
        self._player2 = None
        self._player1 = Player(ctx.author, 
                               discord.utils.get(ctx.guild.channels, name="player-1"))

        embed = Embed(title=f'{self._player1.name} is challenging you to a game of battleships!', 
                      description="Press the ✅-button to join\n Press the ❓-button to learn the rules", 
                      color=0x2d8bfc)

        embed.set_image(url='https://cf.geekdo-images.com/oWcB33sfig9QF_KBEv7iLQ__opengraph/img/m_neU1NRoM71QTaLXJg9F_f0wY4=/fit-in/1200x630/filters:strip_icc()/pic2439783.png')

        components = [[
                    Button(custom_id='accept',
                        emoji='✅',
                        style=ButtonStyle.grey),
                    Button(custom_id='info',
                        emoji='❓',
                        style=ButtonStyle.grey)
            ]]

        message = await ctx.send(embed=embed, components=components)

        def check(i):
            ''' Checking that the right user clicks a button and that is's the right message
                    :parameters:
                        i: potential interaction element
            '''
            return i.author != ctx.author and i.message == message

        while self._player2 == None:
            #waiting for interaction
            interaction = await self._client.wait_for('button_click', check = check)
            i_id = interaction.custom_id

            if i_id == 'accept':
                self._player2 = Player(interaction.author, 
                                       discord.utils.get(ctx.guild.channels, name="player-2"))
                components[0][0].disabled = True
                await message.edit(embed=embed, components=components)
            
            await self.remove_warning(interaction)

        await self._player1.member.add_roles(discord.utils.get(ctx.guild.roles, name="Player1"))
        await self._player2.member.add_roles(discord.utils.get(ctx.guild.roles, name="Player2"))

        await ctx.send(embed=Embed(description='You can now join your game room!'))

        await self.setup()

    async def setup(self):

        await self._player1.channel.purge(limit=None,  check=lambda msg: not msg.pinned)
        await self._player2.channel.purge(limit=None,  check=lambda msg: not msg.pinned)

        #⬛️🟦⬜️🟥
        map = []

        for _ in range(14):
            temp_map = []
            for _ in range(14):
                temp_map.append('🟦')
            map.append(temp_map)

        #setup player 1
        self._player1.status = 'Shooting'
        self._player1.map = [x[:] for x in map]
        self._player1.embed = Embed()
        self._player1.embed.add_field(name='Stats', value=f'💚 Health: {self._player1.health} \n 🔥 Hits: {len(self._player1.hits)}', inline=True)
        self._player1.embed.add_field(name='Status', value=f'Your state: {self._player1.status} \n Last shoot was: ', inline=True)
        self._player1.embed.description = self.update_board(self._player1.map)
        self._player1.embed.title = f'Playing against: {self._player2.name}'

        #setup player 2
        self._player2.status = 'Waiting'
        self._player2.map = [x[:] for x in map]
        self._player2.embed = Embed()
        self._player2.embed.add_field(name='Stats', value=f'💚 Health: {self._player2.health}  \n 🔥 Hits: {len(self._player2.hits)}', inline=True)
        self._player2.embed.add_field(name='Status', value=f'{self._player2.status} \n Last shoot was: ', inline=True)
        self._player2.embed.description = self.update_board(self._player2.map)
        self._player2.embed.title = f'Playing against: {self._player1.name}'

        await self.place_boats(self._player1)
        await self.place_boats(self._player2)

        self.update_health_board(self._player1)
        self.update_health_board(self._player2)

        self._player1.message = await self._player1.channel.send(embed=self._player1.embed, components=self._player1.components)
        self._player2.message = await self._player2.channel.send(embed=self._player2.embed, components=self._player2.components)

        await self.shoot('player-1', 'a1')

    def update_health_board(self, player:Player):
        player.embed.set_field_at(0, name=player.embed.fields[0].name, value=f' 💚 Health: {player.health}  \n 🔥 Hits: {len(player.hits)}', inline=player.embed.fields[0].inline)
    
    def update_status_board(self, player:Player, last:str):
        player.embed.set_field_at(1, name=player.embed.fields[1].name, value=f'Your state: {player.status} \n Last shoot was: {last}', inline=player.embed.fields[0].inline)

    def update_board(self, map:list):
        map_spaces = []
        for y in range(14):
            temp_str = ''
            for x in range(14):
                temp_str += map[y][x] + ' \a '
            map_spaces.append(temp_str)

        board = f''' \a\a\a\a\a\a\a a \a\a\a b \a\a\a\a c \a\a\a d \a\a\a\a e \a\a\a f \a\a\a\a g \a\a\a h \a\a\a\a i \a\a\a\a j \a\a\a\a k \a\a\a\a l \a\a\a m \a\a\a n

                     1 \a\a\a\a {map_spaces[0]}

                     2\a\a\a\a {map_spaces[1]}

                     3\a\a\a\a {map_spaces[2]}

                     4\a\a\a\a {map_spaces[3]}

                     5\a\a\a\a {map_spaces[4]}

                     6\a\a\a\a {map_spaces[5]}

                     7\a\a\a\a {map_spaces[6]}

                     8\a\a\a\a {map_spaces[7]}

                     9\a\a\a\a {map_spaces[8]}

                     10\a\a\a {map_spaces[9]}

                     11 \a\a\a {map_spaces[10]}

                     12\a\a\a {map_spaces[11]}

                     13\a\a\a {map_spaces[12]}

                     14\a\a\a {map_spaces[13]}
        '''

        return board

    def split_list(self, lst):
        half = len(lst)//2
        return lst[:half], lst[half:]

    async def place_boats(self, player:Player):
        '''
        Map:                                Splitting map like this (grid):
                                                l_rows         r_rows
                                                  0              1
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x        
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x      0  x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x      1  x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x
        x x x x x x x x x x x x x x         x x x x x x x  x x x x x x x
        x x x x x x x x x x x x x x      2  x x x x x x x  x x x x x x x
                                            x x x x x x x  x x x x x x x
                                            x x x x x x x  x x x x x x x   

        Ships:
        nr: 0   1   2   3   4   5
            - small -   -- big --
            x   x   x   x   xx  x
            x   x   x   x   xx  x
            x   x   x   x   xx  x
                x   x   x   xx  x
                        x   xx  x
                                x

        Ship placements rules:
            Every ship will be placed in one cell each in the grid,
            ship 3, 4 & 5 can not be placed with all rotations in cell (2, 0) and (2, 1),
            that means that thoes ships have to be placed in any of the other cells,
            the other ships can be placed with any rotation in any cell

        '''

        #placing ships

        small_ships = [[(1, 3), (3, 1)], [(1, 4), (4, 1)], [(1, 4), (4, 1)]] 
        big_ships = [[(1, 5), (5, 1)], [(2, 5), (5, 2)], [(6, 1)]]

        big_cells = [(0, 0), (1, 0), 
                     (0, 1), (1, 1)]

        small_cells = [(0, 2), (1, 2)]

        grid_map_converter = {(0, 0): (0, 0), (1, 0): (7, 0),
                              (0, 1): (0, 5), (1, 1): (7, 5),
                              (0, 2): (0, 10), (1, 2): (7, 10)}

        cell_y_size = {(0, 0): 5, (1, 0): 5,
                       (0, 1): 5, (1, 1): 5,
                       (0, 2): 4, (1, 2): 4}



        small_to_big = small_ships.pop(randint(0, len(small_ships)-1))
        big_ships.append(small_to_big)


        positions = []

        def ship_positions(cells, ships):
            temp_ship_positions = []
            for s in ships:
                ship = s[randint(0, len(s)-1)]
                cell = cells[randint(0, len(cells)-1)]
                cells.remove(cell)
                start_pos = (randint(0, 7-ship[0]), randint(0, cell_y_size[cell]-ship[1]))
                for ship_y in range(ship[1]):
                    for ship_x in range(ship[0]):
                        add_x, add_y = grid_map_converter[cell]
                        x = start_pos[0] + ship_x + add_x
                        y = start_pos[1] + ship_y + add_y
                        temp_ship_positions.append((x, y))            
            return temp_ship_positions


        for pos in ship_positions(big_cells, big_ships):
            positions.append(pos)

        for pos in ship_positions(small_cells, small_ships):
            positions.append(pos)


        player.boat_positions = positions

    #@commands.command(aliases=['s'])
    async def shoot(self, channel:str, cord:str):
        alphabeth = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, 'i':8, 'j':9, 'k':10, 'l':11, 'm':12, 'n':13}
        row = alphabeth[cord[0]]
        column = int(cord[1:]) - 1
        pos = [column, row]


        players = {'player-1':self._player1, 'player-2':self._player2}

        player:Player = players.pop(channel)
        oponent:Player = list(players.values())[0]

        if player.status != 'Shooting':
            return

        if pos in player.shots:
            return

        player.status = 'Waiting'
        oponent.status = 'Shooting'

        #buttons
        def check(i):
            ''' Checking that the right user clicks a button and that is's the right message
                    :parameters:
                        i: potential interaction element
            '''
            return i.message == player.message

        button_movement = {'up':(-1, 0), 'down':(1, 0), 'left':(0, -1), 'right':(0, 1), 'up_left':(-1, -1), 'up_right':(-1, 1), 'down_left':(1, -1), 'down_right':(1, 1)}
        selecting = True
        origional_map = [row[:] for row in  player.map]

        player.map[pos[0]][pos[1]] = '⬜️'
        player.embed.description = self.update_board(player.map)
        await player.message.edit(embed=player.embed, components=player.components)

        while selecting:
            #waiting for interaction
            interaction = await self._client.wait_for('button_click', check = check)
            i_id = interaction.custom_id

            if i_id == 'shoot':
                selecting = False
            else:
                for i, add in enumerate(button_movement[i_id]):
                    if (pos[i] == 0 and add == -1) or (pos[i] == 13 and add == 1):
                        pass
                    else:#if pos[i] >= 0 and add == 0:
                        pos[i] += add
                
                player.map = [row[:] for row in origional_map]
                player.map[pos[0]][pos[1]] = '⬜️'
                player.embed.description = self.update_board(player.map)
                await player.message.edit(embed=player.embed, components=player.components)

            await self.remove_warning(interaction)            

        pos = tuple(pos)
        column, row = pos

        #old
        player.add_shot(pos)

        if pos in oponent.boat_positions:
            player.map[column][row] = '🔥'
            player.add_hit(pos)
            oponent.remove_boat_position(pos)
            self.update_status_board(player, 'Hit!')
            self.update_status_board(oponent, 'Hit!')
        else:
            player.map[column][row] = '🟥'
            self.update_status_board(player, 'Miss!')
            self.update_status_board(oponent, 'Miss!')


        player.embed.description = self.update_board(player.map)
        self.update_health_board(player)
        await player.message.edit(embed=player.embed, components=player.components)


        self.update_health_board(oponent)
        await oponent.message.edit(embed=oponent.embed, components=oponent.components)

        if oponent.health <= 0:
            await self.winner(player, oponent)
        else:
            await self.shoot(oponent.channel.name, 'a1')

    async def winner(self, winner:Player, loser:Player):
        embed = Embed(title=f'{winner.name} has defeated {loser.name}')
        await winner.channel.send(embed=embed)
        await loser.channel.send(embed=embed)

def setup(client):
    client.add_cog(Game(client))
































































'''

        grid = []
        splits = [4, 9, 13]
        temp_left = []
        temp_right = []

        l_rows = []
        r_rows = []

        deviding the map

        for row in player.map:
            l_row, r_row = self.split_list(row)
            l_rows.append(l_row)
            r_rows.append(r_row)


        for i, (l_row, r_row) in enumerate(zip(l_rows, r_rows)):
            temp_left.append(l_row)
            temp_right.append(r_row)
            if i in splits:
                grid.append([temp_left, temp_right])
                temp_left = []
                temp_right = []


---------------------------------------------------------------------



        for pos in player.boat_positions:
            player.map[pos[0]][pos[1]] = '⬛️'

        player.embed.description = self.update_board(player.map)

        await player.message.edit(embed=player.embed)

'''