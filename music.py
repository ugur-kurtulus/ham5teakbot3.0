from discord.ext import commands
import lavalink
import discord
from discord import utils
from discord import Embed
import math

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7484, 'youshallnotpass', 'tr', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
    
    @commands.command(name='join')
    async def join(self, ctx):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(vc.id))
            
    @commands.command(name='disconnect', aliases=['dc'])
    async def disconnect(self,ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send('Not connected.')
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voicechannel!')
        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)
        embed = Embed(color=discord.Color.dark_teal())
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        embed.description = f"Bot disconnected from voice channel."
        await ctx.channel.send(embed=embed)

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.shuffle()
        await ctx.send("Queue shuffled.")

    @commands.command(name="stop")
    async def stop_command(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.queue.empty()
        await player.stop()
        await ctx.send("Playback stopped.")

    @commands.command(name="next", aliases=["skip", "s"])
    async def next_command(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.skip()
        embed = Embed(color=discord.Color.dark_teal())
        embed.description = f"[{player.current.title}](https://youtube.com/watch?v={player.current.identifier}) is now playing!"
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.channel.send(embed=embed)

    @commands.command(name="current",aliases=['np','nowplaying'])
    async def current(self,ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        embed = Embed(color=discord.Color.dark_teal())
        embed.description = f"[{player.current.title}](https://youtube.com/watch?v={player.current.identifier}) is playing."
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.channel.send(embed=embed)

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'{index + 1}. [**{track.title}**]({track.uri})\n'
        embed = discord.Embed(colour=discord.Color.dark_teal(),
        description=f'**{len(player.queue)} upcoming tracks**\n\n[{player.current.title}](https://youtube.com/watch?v={player.current.identifier}) is playing.\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name='search', aliases=["ps"])
    async def search(self, ctx, *, query):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(vc.id))
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:10]
            i = 0
            query_result = ''
            for track in tracks:
                i = i + 1
                trackurl = track["info"]["uri"]
                tracktitle = track["info"]["title"] 
                query_result = query_result + f'{i}) [{tracktitle}]({trackurl})\n'
            embed = Embed(color=discord.Color.dark_teal())
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            embed.description = query_result

            await ctx.channel.send(embed=embed)

            def check(m):
                return m.author.id == ctx.author.id
      
            response = await self.bot.wait_for('message', check=check)
            track = tracks[int(response.content)-1]
            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()
            embed = Embed(color=discord.Color.dark_teal())
            trackurl = track["info"]["uri"]
            tracktitle = track["info"]["title"] 
            embed.description = f"[{tracktitle}]({trackurl}) has successfully been added to queue!"
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.channel.send(embed=embed)
        except Exception as error:
            print(error)

    @commands.command(name='play', aliases=["p"])
    async def play(self, ctx, *, query):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(vc.id))
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:1]
            track = tracks[0]
            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()
            embed = Embed(color=discord.Color.dark_teal())
            trackurl = track["info"]["uri"]
            tracktitle = track["info"]["title"] 
            embed.description = f"[{tracktitle}]({trackurl}) has successfully been added to queue!"
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.channel.send(embed=embed)
        except Exception as error:
            print(error)
    
    @play.error
    async def play_command_error(self, ctx, exc):
        print(exc)

    @search.error
    async def play_command_error(self, ctx, exc):
        print(exc)
        
    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

def setup(bot):
  bot.add_cog(MusicCog(bot))