import os

import discord
from discord.ext import commands

import youtube_dl
import asyncio

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        print('ok')
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, client):
        self._client = client
        
    @commands.command()
    async def join(self, ctx):
        voice_channel:discord.channel.VoiceChannel = discord.utils.get(ctx.guild.voice_channels, name=ctx.channel.name)
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        if voice == None:
            await voice_channel.connect()
        else:
            await ctx.message.reply('Bot is alredy connected to a voice channel')

    @commands.command()
    async def leave(self, ctx):
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_connected() and ctx.channel.name == voice.channel.name:
                await voice.disconnect()
        else:
            await ctx.message.reply('Bot is not connected to a voice channel')

    @commands.command()
    async def pause(self, ctx):
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_playing():
                await voice.disconnect()
            else:
                await ctx.message.reply('Bot is currently not playing')
        else:
            await ctx.message.reply('Bot is not connected to a voice channel')

    @commands.command()
    async def resume(self, ctx):
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_paused():
                await voice.resume()
            else:
                await ctx.message.reply('Bot has not been paused')
        else:
            await ctx.message.reply('Bot is not connected to a voice channel')

    @commands.command()
    async def stop(self, ctx):
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        if voice:
            voice.stop()
        else:
            await ctx.message.reply('Bot is not connected to a voice channel')

    @commands.command()
    async def play(self, ctx, url):
        #voice_channel:discord.channel.VoiceChannel = discord.utils.get(ctx.guild.voice_channels, name=ctx.channel.name)
        voice:discord.voice_client.VoiceClient = discord.utils.get(self._client.voice_clients, guild=ctx.guild)

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self._client.loop)
            voice.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

def setup(client):
    client.add_cog(Music(client))

















































'''

        song_exists = os.path.isfile('./music_file/song.mp3')
        print(song_exists)
        try:
            if song_exists:
                os.remove("./music_file/song.mp3")
        except PermissionError:
            await ctx.message.reply('Wait for the current playing music to end or use the "stop" command')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            #ydl.download([url])
            pass

        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.rename(file, 'song.mp3')
                os.replace('./song.mp3', './music_file/song.mp3')
'''