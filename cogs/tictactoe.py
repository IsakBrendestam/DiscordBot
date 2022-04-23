import imp
from multiprocessing.spawn import import_main_path
from shutil import move
from typing import List
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select, SelectOption
import discord

class Player:
    def __init__(self, member):
        self._moves = {(1, 1):0, (2, 1):0, (3, 1):0,
                       (1, 2):0, (2, 2):0, (3, 2):0,
                       (1, 3):0, (2, 3):0, (3, 3):0}
        self._member = member

    @property
    def member(self) -> discord.Member:
        return self._member

    @property
    def moves(self) -> list:
        return self._moves

    def add_move(self, move:list):
        self._moves[move] = 1

class Game(commands.Cog):
    def __init__(self, client):
        self._client = client
        
    async def remove_warning(self, interaction):
        ''' Removes the warning from a interaction
                :Parameters:
                    interaction: the interaction that the user interacted with
        '''
        try:
            await interaction.respond()
        except:
            pass

    @commands.command()
    async def ttt(self, ctx):

        self._player1 = Player(ctx.author)
        self._player2:Player = None

        components = components = [[
                    Button(custom_id='11',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='21',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='31',
                        label='\a',
                        style=ButtonStyle.grey)],
                [
                    Button(custom_id='12',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='22',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='32',
                        label='\a',
                        style=ButtonStyle.grey)],
                [
                    Button(custom_id='13',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='23',
                        label='\a',
                        style=ButtonStyle.grey),
                    Button(custom_id='33',
                        label='\a',
                        style=ButtonStyle.grey)]]

        message = await ctx.send(components = components)
        player_switch = True
        players = {True:self._player1}

        def check(i):
                ''' Checking that the right user clicks a button and that is's the right message
                        :parameters:
                            i: potential interaction element
                '''
                if player_switch:
                    return i.author == self._player1.member and i.message == message

                if self._player2 == None:
                    self._player2 = Player(i.author)
                    players[False] = self._player2

                return i.author == self._player2.member and i.message == message

        
        
        turns = 0
        playing = True
        while playing:
            #waiting for interaction
            interaction = await self._client.wait_for('button_click', check=check)

            # if not player_switch and self._player2 == None:
            #     self._player2 = Player(interaction.author)
            #     players[False] = self._player2

            current_player = players[player_switch]

            i_id = interaction.custom_id
            for comp_list in components:
                for component in comp_list:
                    if component.custom_id == i_id:
                        if player_switch:
                            component.label = '❌'
                        else:
                            component.label = '⭕️'

                        current_player.add_move(tuple(map(int, i_id)))
                        component.disabled = True
                        
            turns += 1
            
            if self.check_winner(current_player):
                for comp_list in components:
                    for component in comp_list:
                        component.disabled = True
                await ctx.send('The winner is: ' + current_player.member.display_name)
                playing = False

            if turns >= 9 and playing:
                await ctx.send('This is a draw!')
                playing = False

            player_switch = not player_switch
            await interaction.message.edit(components=components)
            await self.remove_warning(interaction)

    def check_winner(self, player:Player):
        moves = player.moves
        win = False

        for i in range(1, 4):
            #horizontal
            if moves[(i, 1)] + moves[(i, 2)] + moves[(i, 3)] == 3:
                win = True
            
            #vertical
            if moves[(1, i)] + moves[(2, i)] + moves[(3, i)] == 3:
                win = True

        if moves[(1, 1)] + moves[(2, 2)] + moves[(3, 3)] == 3:
            win = True

        if moves[(3, 1)] + moves[(2, 2)] + moves[(1, 3)] == 3:
            win = True

        return win


        

def setup(client):
    client.add_cog(Game(client))













































'''
winner = False

x_cords = []
y_cords = []

diag_count = 0

for move in player.moves:
    x, y = move
    x_cords.append(x)
    y_cords.append(y)

    if x == y or x == y+2 or x+2 == y:
        diag_count += 1

if diag_count == 3:
    return True

x_unique = list(set(x_cords))
y_unique = list(set(y_cords))

for x, y in zip(x_unique, y_unique):
    if x_cords.count(x) == 3 or y_cords.count(y) == 3:
        winner = True

return winner
'''