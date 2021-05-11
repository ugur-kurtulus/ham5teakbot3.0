import os
from dotenv import load_dotenv
from discord.utils import get  # New import
import discord
from discord.ext import commands  # New import
from discord_slash import SlashCommand, SlashContext
from mcstatus import MinecraftServer
import asyncio
import sys
import sqlite3

client = commands.Bot(command_prefix='-')  # Defines prefix and bot
slash = SlashCommand(client, sync_commands=False)  # Defines slash commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

async def my_background_task():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
            guild_id INTEGER,
            statuschannel_id INTEGER,
            alertschannel_id INTEGER,
            lpalertschannel_id INTEGER,
            crashalertschannel_id INTEGER,
            tc INTEGER,
            svc INTEGER,
            sbc INTEGER,
            facc INTEGER,
            svsvc INTEGER,
            crc INTEGER,
            prc INTEGER,
            cbc INTEGER,
            dcc INTEGER,
            cc INTEGER,
            hsc INTEGER,
            bugc INTEGER,
            imptc INTEGER,
            eventc INTEGER, 
            mgc INTEGER,
            moderator INTEGER
        )
    ''')
    for guild in client.guilds:
        cursor.execute(f"SELECT statuschannel_id FROM main WHERE guild_id = {guild.id}")
        statuschannel = cursor.fetchone()
        if statuschannel[0] is not None:
            channel = client.get_channel(statuschannel[0])
            await channel.purge(limit=10)
            server = MinecraftServer.lookup("play.ham5teak.xyz:25565")
            status = server.status()
            if status.latency >= 1:
                ham5teak = "Online ✅"
            else:
                ham5teak = "Offline ❌"
            embed = discord.Embed(description=f"**Ham5teak Status:** {ham5teak} \n **Players:** {status.players.online}\n**IP:** play.ham5teak.xyz\n**Versions:** 1.13.x, 1.14.x, 1.15.x, 1.16.x", color=discord.Color.teal())
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            embed.set_author(name="Ham5teak Network Status", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
            await channel.send(embed=embed)
            print(f"{guild.name} status successfully sent!")
        else:
            print(f"{guild.name} hasn't assigned any channels to status.")
    await asyncio.sleep(600)

@client.event
async def on_ready():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
            guild_id INTEGER,
            statuschannel_id INTEGER,
            alertschannel_id INTEGER,
            lpalertschannel_id INTEGER,
            crashalertschannel_id INTEGER,
            tc INTEGER,
            svc INTEGER,
            sbc INTEGER,
            facc INTEGER,
            svsvc INTEGER,
            crc INTEGER,
            prc INTEGER,
            cbc INTEGER,
            dcc INTEGER,
            cc INTEGER,
            hsc INTEGER,
            bugc INTEGER,
            imptc INTEGER,
            eventc INTEGER,
            mgc INTEGER,
            moderator INTEGER
        )
    ''')
    print('Logged on as {0}!'.format(client.user.name))
    activity = discord.Game(name="play.ham5teak.xyz")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print("Presence has been set!")
    message = ""
    for guild in client.guilds:
        message += f"{guild.name}\n"
    channel = client.get_channel(841245744421273620)
    embed = discord.Embed(description=f"**__Guilds:__ **\n{message}", color=discord.Color.teal())
    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
    await channel.send(embed=embed)
    print(f"Guilds:\n{message}")
    for guild in client.guilds:
        await my_background_task()

@client.command()
async def edit(ctx, id, new):
    await ctx.message.delete()
    tobeedited = ctx.channel.get_partial_message(id)
    newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
    newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
    await tobeedited.edit(embed = newEmbed)

@client.command()
async def setchannel(ctx, arg1, arg):
    await ctx.message.delete()
    commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel"]
    for command in commandsloop:
        if arg1 == command:
            db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT statuschannel_id FROM main WHERE guild_id = {ctx.guild.id}")
        result =  cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, statuschannel_id) VALUES(?,?)")
            val = (ctx.guild.id, arg)
        elif result is not None:
            sql = ("UPDATE main SET statuschannel_id = ? WHERE guild_id = ?")
            val = (arg, ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        

@edit.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.delete()
        error = await ctx.send('Please specify the amount of message you would like to edit. `-edit <messageid> <newmessage>`')
        await asyncio.sleep(5)
        await error.delete()
    if isinstance(error, commands.CommandInvokeError):
        error = await ctx.send('Please enter a valid message ID.')
        await asyncio.sleep(5)
        await error.delete()

@setchannel.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.delete()
        error = await ctx.send('Please specify the channel you would like to set. `-setchannel <channel> <id>`')
        await asyncio.sleep(5)
        await error.delete()

@client.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.defer(hidden=True)
        embed = discord.Embed(description=f"Please make sure you have entered all values correctly.\n {error}", color=ctx.author.color)
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.send(embed=embed, hidden=True)

@slash.slash(name="setchannel", description="Set channels for your server")
@commands.has_permissions(manage_guild=True)
async def tag(ctx, channel, value):
    if ctx.channel.type is discord.ChannelType.private:
        return
    await ctx.defer(hidden=True)
    commandsloop = ["statuschannel_id", "alertschannel_id", "lpalertschannel_id", "crashalertschannel_id", "tc", "svc",
    "sbc", "svsvc", "facc", "prc", "crc", "cbc", "dcc", "cc", "bugc", "imptc", "hsc", "eventc"]
    for command in commandsloop:
        if channel == command:
            if value == "Null" or value == "null":
                db = sqlite3.connect('main.sqlite')
                cursor = db.cursor()
                cursor.execute(f"SELECT {channel} FROM main WHERE guild_id = {ctx.guild.id}")
                result =  cursor.fetchone()
                if result is None:
                    return
                elif result is not None:
                    cursor.execute(f"SELECT {channel} FROM main WHERE guild_id = {ctx.guild.id}")
                    result =  cursor.fetchone()
                    chanid = result[0]
                    sql = (f"UPDATE main SET {channel} = NULL where {channel} = {chanid}")
                    cursor.execute(sql)
                    db.commit()
                    embed = discord.Embed(description=f"{channel} has been unset.", color=ctx.author.color)
                    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                    await ctx.send(embed=embed)
                    return
            else:
                a = int(value)
                if client.get_channel(a) is not None:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()
                    cursor.execute(f"SELECT {channel} FROM main WHERE guild_id = {ctx.guild.id}")
                    result =  cursor.fetchone()
                    if result is None:
                        sql = (f"INSERT INTO main(guild_id, {channel}) VALUES(?,?)")
                        val = (ctx.guild.id, value)
                    elif result is not None:
                        sql = (f"UPDATE main SET {channel} = ? WHERE guild_id = ?")
                        val = (value, ctx.guild.id)
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    embed = discord.Embed(description=f"{value} has been set as {channel}", color=ctx.author.color)
                    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                    await ctx.send(embed=embed)
                    return
                else:
                    embed = discord.Embed(description=f"Channel ID {value} is not valid.", color=ctx.author.color)
                    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                    await ctx.send(embed=embed)

@slash.slash(name="setrole", description="Set roles for your server")
@commands.has_permissions(manage_guild=True)
async def tag(ctx, moderator):
    if ctx.channel.type is discord.ChannelType.private:
        return
    await ctx.defer(hidden=True)
    moderator1 = moderator.id
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT moderator FROM main WHERE guild_id = {ctx.guild.id}")
    result =  cursor.fetchone()
    if result is None:
        sql = (f"INSERT INTO main(guild_id, moderator) VALUES(?,?)")
        val = (ctx.guild.id, moderator1)
    elif result is not None:
        sql = (f"UPDATE main SET moderator = ? WHERE guild_id = ?")
        val = (moderator1, ctx.guild.id)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()
    embed = discord.Embed(description=f"{moderator} has been set as moderator role.", color=ctx.author.color)
    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
    await ctx.send(embed=embed)

@slash.slash(name="tag", description="A command used to leave a note to a channel")
async def tag(ctx, note, user = None, channel = None, rolei = None):
    if ctx.channel.type is discord.ChannelType.private:
        return
    await ctx.defer(hidden=False)
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT moderator FROM main WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()
    if result[0] is None:
        embed = discord.Embed(description=f"You don't have a moderator role set.", color=ctx.author.color)
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.send(embed=embed, hidden=True)
        return
    elif result is not None:
        role = result[0]
        role1 = discord.utils.get(ctx.guild.roles, id=role)
        if role1 in ctx.author.roles:
            if user is not None:
                embed = discord.Embed(description=f"{ctx.author.mention} has tagged the channel as `{note.upper()}` {user.mention}", color=ctx.author.color)
                embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            elif channel is not None:
                embed = discord.Embed(description=f"{ctx.author.mention} has tagged the channel as `{note.upper()}` {channel.mention}", color=ctx.author.color)
                embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            elif rolei is not None:
                embed = discord.Embed(description=f"{ctx.author.mention} has tagged the channel as `{note.upper()}` {rolei.mention}", color=ctx.author.color)
                embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            else:
                embed = discord.Embed(description=f"{ctx.author.mention} has tagged the channel as `{note.upper()}`", color=ctx.author.color)
                embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.send(embed=embed)
                    
@slash.slash(name="edit", description="Edit an embed sent by the bot")
async def tag(ctx: SlashContext, messageid, new):
    if ctx.channel.type is discord.ChannelType.private:
        return
    await ctx.defer(hidden=True)
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT moderator FROM main WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()
    if result[0] is None:
        embed = discord.Embed(description=f"You don't have a moderator role set.", color=ctx.author.color)
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.send(embed=embed)
        return
    elif result is not None:
        role = result[0]
        role1 = discord.utils.get(ctx.guild.roles, id=role)
        if role1 in ctx.author.roles:
            tobeedited = ctx.channel.get_partial_message(messageid)
            newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
            newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await tobeedited.edit(embed = newEmbed)
            embed = discord.Embed(description=f"Message `{messageid}` has been edited", color=ctx.author.color)
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.send(embed=embed, hidden=True)
        else:
            embed = discord.Embed(description=f"Only <@&{role1.id}> has permission to use this command.", color=ctx.author.color)
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.send(embed=embed)            

@slash.slash(name="ham5teak", description="View Ham5teak network status")
async def tag(ctx):
    server = MinecraftServer.lookup("play.ham5teak.xyz:25565")
    status = server.status()
    if status.latency >= 1:
        ham5teak = "Online ✅"
    else:
        ham5teak = "Offline ❌"
    print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
    embed = discord.Embed(description=f"**Ham5teak Status:** {ham5teak} \n **Players:** {status.players.online}", color=ctx.author.color)
    embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
    embed.set_author(name="Ham5teak Network Status", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
    await ctx.send(embed=embed)

@slash.slash(name="move", description="Move a channel to speciified")
async def tag(ctx: SlashContext, category):
    if ctx.channel.type is discord.ChannelType.private:
        return
    await ctx.defer(hidden=True)
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT moderator FROM main WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()
    if result[0] is None:
        embed = discord.Embed(description=f"You don't have a moderator role set.", color=ctx.author.color)
        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
        await ctx.send(embed=embed)
        return
    elif result is not None:
        role = result[0]
        role1 = discord.utils.get(ctx.guild.roles, id=role)
        if role1 in ctx.author.roles:
            commandsloop = ["tc", "svc","sbc", "svsvc", "facc", "prc", "crc", "cbc", "dcc", "cc", "bugc", "imptc", 
            "hsc", "eventc", "mgc"]
            for command in commandsloop:
                if category == command:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()
                    cursor.execute(f"SELECT {category} FROM main WHERE guild_id = {ctx.guild.id}")
                    result = cursor.fetchone()
                    if result[0] is None:
                        embed = discord.Embed(description=f"You don't have a {category} category set.", color=ctx.author.color)
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        await ctx.send(embed=embed)
                    elif result is not None:
                        ctxchannel = ctx.channel
                        categorya = int(result[0])
                        cat = client.get_channel(categorya)
                        await ctxchannel.edit(category=cat)
                        discordstaff = discord.utils.get(ctx.guild.roles, name="Discord Staff")
                        embed = discord.Embed(description=f"#{ctxchannel} has been moved to category {cat}", color=ctx.author.color)
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        await ctx.send(embed=embed)
                        if category == "hsc":
                            if get(ctx.guild.roles, name="Staff"):
                                staff = discord.utils.get(ctx.guild.roles, name="Staff")
                                await ctxchannel.set_permissions(staff, view_channel=False)
                            if get(ctx.guild.roles, name="Discord Staff"):
                                staff = discord.utils.get(ctx.guild.roles, name="Discord Staff")
                                await ctxchannel.set_permissions(staff, view_channel=False)
                        else:
                            if get(ctx.guild.roles, name="Staff"):
                                staff = discord.utils.get(ctx.guild.roles, name="Staff")
                                await ctxchannel.set_permissions(staff, view_channel=True)
                            if get(ctx.guild.roles, name="Discord Staff"):
                                staff = discord.utils.get(ctx.guild.roles, name="Discord Staff")
                                await ctxchannel.set_permissions(staff, view_channel=True)
        else:
            embed = discord.Embed(description=f"Only <@&{role1.id}> has permission to use this command.", color=ctx.author.color)
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            await ctx.send(embed=embed)

@client.event
async def on_message(message):
    if message.channel.type is discord.ChannelType.private:
        return
    channelnames = ["announcements", "updates", "competitions", "events"]
    for channel in channelnames:
        if channel in message.channel.name:
            if not message.author.bot:
                if message.content.startswith('-edit'):
                    return
                else:
                    if message.attachments:
                        await message.attachments[0].save(f"./{message.attachments[0].filename}")
                        file = discord.File(message.attachments[0].filename)
                        embed = discord.Embed(description=f"{message.content}", color=message.author.color)
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        embed.set_image(url=f"attachment://{message.attachments[0].filename}")
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        msg = await message.channel.send(embed=embed, file=file)
                        await msg.add_reaction("👍")
                        await msg.add_reaction("❤️")
                        print(f"An image inclusive announcement was made in #{message.channel.name} by {message.author}.")
                        await message.delete()
                        os.remove(f"./{message.attachments[0].filename}")
                    if not message.attachments:
                        await message.delete()
                        embed = discord.Embed(description=f"{message.content}", color=message.author.color)
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        msg = await message.channel.send(embed=embed)
                        await msg.add_reaction("👍")
                        await msg.add_reaction("❤️")
                        print(f"An announcement was made in #{message.channel.name} by {message.author}.")
    channelnames = ["suggestions", "polls"]
    for channel in channelnames:
        if channel in message.channel.name:
            if not message.author.bot:
                if message.content.startswith('-edit'):
                    return
                else:
                    if message.attachments:
                        await message.attachments[0].save(f"./{message.attachments[0].filename}")
                        file = discord.File(message.attachments[0].filename)
                        embed = discord.Embed(description=f"{message.content}", color=message.author.color)
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        embed.set_image(url=f"attachment://{message.attachments[0].filename}")
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        msg = await message.channel.send(embed=embed, file = file)
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❌")
                        print(f"An image inclusive suggestion was made in #{message.channel.name} by {message.author}.")
                        await message.delete()
                        os.remove(f"./{message.attachments[0].filename}")
                    if not message.attachments:
                        await message.delete()
                        embed = discord.Embed(description=f"{message.content}", color=message.author.color)
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
                        msg = await message.channel.send(embed=embed)
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❌")
                        print(f"An suggestion was made in #{message.channel.name} by {message.author}.")
    await client.process_commands(message)

client.run(TOKEN)  # Changes
