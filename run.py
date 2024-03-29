import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import urllib.parse, urllib.request
import re
import json
from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': False,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4
}

ffmpeg_options = {
    'options': ''
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

client = commands.Bot(command_prefix='seulgi ')

status = ['seulgi queue **url/song name**', 'seulgi view', 'seulgi play ~Song Name~']
queue = []

@client.event
async def on_ready():
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `Seulgi help` command for details!')
        
@client.command(name='ping', help='Seulgi returns your latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='Seulgi choose a random hello message for you')
async def hello(ctx):
    responses = ['***grumble*** Why did you wake me up?', 'Top of the morning to you lad!', 'Hello, how are you?', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name="quem", help='This returns the true love')
async def teamo(ctx, *args):
    buf=""
    for x in args:
        buf+= x + " "
    buf = buf[:-1]
    if buf=="e meu amor":
        await ctx.send('tami')
    else:
        await ctx.send("quem?")

@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Você não está em um canal, e se nos encontrassemos no Geral? 👉👈")
        return
    
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    
@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url, *args):
    global queue
    helptext = url
    for word in args:
        helptext+= word

    queue.append(helptext)
    await ctx.send(f'`{queue[0]}` added to queue!')

@client.command(name='skip', help='This command skip a song')
async def skip(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client
    if (len(queue)):
        async with ctx.typing():
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            voice_channel.source = player

        await ctx.send('Now playing: {}'.format(player.title))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=('{}'.format(player.title))))
        del(queue[0])
    else:
        await ctx.send("**Your queue is empty!**")

@client.command(name='remove', help='This command removes an item from the list')
async def remove(ctx, number):
    global queue
    try:
        del(queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')

    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')

@client.command(name='play', help='This command plays songs')
async def play(ctx, url=None,*args):
    global queue
    try:
        await ctx.invoke(client.get_command('join'))
    except:
        pass #Seulgi is already at the channel

    server = ctx.message.guild
    voice_channel = server.voice_client
    helptext = url
    for word in args:
        helptext+= ' '+word

    queue.append(helptext)
    if voice_channel.is_playing():
        await ctx.send(f'`{queue[len(queue)-1]}` added to queue!')
        return

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        playing.start(ctx)
    await ctx.send('**Now playing:** {}'.format(player.title))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=('{}'.format(player.title))))
    del(queue[0])

@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    playing.cancel()
    voice_channel.pause()

@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    playing.start(ctx)
    voice_channel.resume()

@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    indexes = list(range(len(queue)))
    pretty_display = dict(zip(indexes,queue))

    await ctx.send(f'Your queue is now:\n```py\n{json.dumps(pretty_display, indent=4)}```')

@client.command(name='leave', help='This command stops makes the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    playing.cancel()
    await voice_client.disconnect()

@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    playing.cancel()
    voice_channel.stop()

@tasks.loop(seconds=1)
async def playing(ctx):
    global queue
    voice_channel = ctx.message.guild.voice_client
    if(voice_channel.is_playing() is False):
        async with ctx.typing():
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('**Now playing:** {}'.format(player.title))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=('{}'.format(player.title))))
        del (queue[0])
    else:
        pass

client.run('') #add your token there and run
