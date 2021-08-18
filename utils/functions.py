import discord
from dotenv import load_dotenv
import asyncio
import os
import mysql.connector
from discord.ext import commands 
from dotenv import load_dotenv
import discord
from discord.ext import commands 
from discord_slash import SlashCommand
from mcstatus import MinecraftServer
import asyncio
import emoji as e
import mysql.connector

"""
Core Keys
"""

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
host = os.getenv("mariadb_host")
port = os.getenv("mariadb_port")
database = os.getenv("mariadb_database")
username = os.getenv("mariadb_username")
password = os.getenv("mariadb_password")

"""
SQL Functions
"""

def sqlconnect(): 
    try:
        mydb = mysql.connector.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
        )
        return mydb
    except mysql.connector.Error as e:
        print(e)
        print('Failed to connect to MySQL')

def createtable(sql,table_name , query):
    tablecursor = sql.cursor()
    tablecursor.execute("SHOW TABLES")  
    tables = []
    for row in tablecursor.fetchall(): 
        tables.append(row[0])
    tablecursor.close()
    if table_name in tables:
        print(f'{table_name} already exists')
        return
    else:
        try:
            with sql.cursor() as cursor:
                cursor.execute(query)
                cursor.close()
                print(f'{table_name} created successfully!')
        except mysql.connector.Error as e:
            print(e)
            print(f'Failed to Create {table_name}')

def deletequery(sql, table , where):
    sql.connect()
    query = (f'DELETE FROM {database}.{table} WHERE {where}') # nosec
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)
            sql.commit()
            querycursor.close()
            return 1
    except mysql.connector.Error as e:
        print(e)
        print(f'Failed to execute delete query')
        return 1
    except TypeError as e:
        return 1

def selectquery(sql, table , column , where):
    sql.connect()
    wherenew = str(where)
    query = (f'SELECT {column} FROM {database}.{table} WHERE {wherenew}')
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)  
            result = querycursor.fetchone()[0]
            sql.commit()
            querycursor.close() 
            return result
    except mysql.connector.Error as e:
        print(e)
        print(f'Failed to execute select query')
        return 1
    except TypeError as e:
        return 1

def selectqueryall(sql, table , column, where):
    sql.connect()
    if where is not None:
        query = (f'SELECT {column} FROM {database}.{table} WHERE {where}')
    if where is None:
        query = (f'SELECT {column} FROM {database}.{table}')
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)  
            result = querycursor.fetchall()
            sql.commit()
            querycursor.close()
            return result
    except mysql.connector.Error as e:
        print(e)
        print(f'Failed to execute select query')
        return 1
    except TypeError as e:
        return 1

def insertquery(sql, table , column , values , where):
    size = len(values)
    sql.connect()
    if where == None:
        query = (f'INSERT INTO {database}.{table} {column} VALUES(%s'+(size-1)*(',%s')+')')
    else:
        query = (f'UPDATE {database}.{table} SET {column} = {values}' + f' WHERE {where}')
    try:
        with sql as sql:
            querycursor = sql.cursor()
            querycursor.execute(query , values)
            sql.commit()
            querycursor.close()
            return 0
    except mysql.connector.Error as e:
        print(e)
        print(f'Failed to execute insert query')
        return 1

quilds_query = (f'''
        CREATE TABLE {database}.guilds
            (guild_id BIGINT NOT NULL PRIMARY KEY,
            guild_name VARCHAR(255) NOT NULL,
            premium BOOLEAN,
            prefix varchar(5) DEFAULT "-",
            administrator_id BIGINT,
            moderator_id BIGINT,
            generalchannel BIGINT,
            statuschannel BIGINT,
            alertschannel BIGINT,
            lpalertschannel BIGINT,
            crashalertschannel BIGINT,
            demandedsuggestions BIGINT,
            acceptedsuggestions BIGINT,
            rejectedsuggestions BIGINT,
            custommovecount INT DEFAULT 0,
            betaannouncements TINYINT)''')
categories_query = (f'''
        CREATE TABLE {database}.categories 
            (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            category_id BIGINT,
            category_name VARCHAR(255),
            category_less VARCHAR(255)
            )''') 
restrict_query = (f'''
        CREATE TABLE {database}.restrict (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            guild_id BIGINT DEFAULT NULL,
            restrictrole_name VARCHAR(255),
            restrictrole_id BIGINT,
            restrictrole2_id BIGINT,
            restrictrole3_id BIGINT
            )''')
passwords_query = (f'''
        CREATE TABLE {database}.passwords (
            guild_id BIGINT DEFAULT NULL,
            password VARCHAR(255),
            used TINYINT
            )''')
announcements_query = (f'''
        CREATE TABLE {database}.announcements
            (guild_id BIGINT DEFAULT NULL,
            channel_id BIGINT,
            channel_type VARCHAR(255)
            )''')

sql = sqlconnect()      
createtable(sql,'guilds', quilds_query)
createtable(sql,'categories', categories_query)
createtable(sql,'restrict', restrict_query)
createtable(sql,'passwords', passwords_query)
createtable(sql, 'announcements', announcements_query)

"""
Arrays and Dicts
"""

colors = {"green": 0x3aa45c, "red": 0xed4344, "blue": 0x5864f3, "aqua": 0x00FFFF, "dark_teal": 0x10816a, "teal": 0x1abc9c, "invis": 0x2f3037}

premium_guilds = [selectqueryall(sql, 'guilds', 'guild_id', None)]

announcementschannels = {}

suggestionchannels = {}

pollchannels = {}

betaannouncementguilds = []

ham_guilds = [380308776114454528, 841225582967783445, 820383461202329671, 789891385293537280, 82038346120232967, 650658756803428381, 571626209868382236, 631067371661950977]

prefixes = {}

def getprefix(client, message):
    if not message.guild:
        return "-"
    if message.guild.id in premium_guilds and message.guild.id not in prefixes:
        pref = selectquery(sql, "guilds", "prefix", f"guild_id={message.guild.id}")
        prefixes.update({f"{message.guild.id}": f"{pref}"})
    elif message.guild.id not in premium_guilds and message.guild.id not in prefixes:
        prefixes.update({f"{message.guild.id}": f"-"})
    return commands.when_mentioned_or(*prefixes[f"{message.guild.id}"])(client, message)

"""
Key definitions
"""

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=(getprefix), intents=intents)  # Defines prefix and bot
slash = SlashCommand(client, sync_commands=False)  # Defines slash commands

"""
Functions
"""

def settitle(embed, titlestr): # Used in one liner for loops
    embed.title = titlestr
    return embed

async def deletemessage(ctx): # Used to delete message avoiding exceptions on missing permission or similar issues
    try:
        await ctx.message.delete()
    except: #nosec
        pass
    return

def clean_code(content): # Used in the evaluate command
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

async def is_owner(ctx, memberid=None):
    developers = [461572795684356098, 610930740422508544, 258530967096918016]
    if memberid == None:
        if ctx.author.id in developers: 
            return True
    elif memberid != None:
        if memberid in developers:
            return True
    else:
        return False

def getprefix2(ctx):
    return prefixes[f"{ctx.guild.id}"]

async def sendwebhook(ctx, webhookname, channel, file, embeds):
    for w in await ctx.guild.webhooks():
        if ctx is None: image = client.user.avatar_url
        if ctx != None: image = ctx.author.avatar_url
        if "Ham5teakBot3" == w.name and w.channel == channel:
            await w.send(username=webhookname, avatar_url=image, embeds=embeds, file=file)
            return True
    webhook = await channel.create_webhook(name="Ham5teakBot3")
    await webhook.send(username=webhookname, avatar_url=image, embeds=embeds, file=file)
    return True

async def getwebhook(ctx, webhookname, channel = None): # Gets webhook object from channel
    if channel == None:
        for w in await ctx.guild.webhooks():
            if webhookname == w.name and w.channel == ctx.channel:
                return w
    else:
        for w in await channel.guild.webhooks():
            if webhookname == w.name and w.channel == channel:
                return w
        
async def nopermission(ctx): # Standard no permission error used in commands
    embedDescription  = (f"You don't have permission to do this.")
    return addEmbed(ctx,None,embedDescription )

async def unknownerror(ctx, error): # Sends the unknown error embed
    return await ctx.send(embed=addEmbed(None, "red", f"`{error}`", None), delete_after=5)

async def stripmessage(string, targetstring): # 
    if targetstring in string:
        stringlist = string.split(f"\n")
        for stringa in stringlist:
            if targetstring in stringa:
                return stringa

def disablebutton(button): # Disables button
    button["disabled"] = True

async def moderatorcheck(guild, member): # Checks if user is a bot moderator
    if not guild:
        return 1
    try:
        if guild.id == 380308776114454528:
            discordstaff = guild.get_role(name="Discord Staff")
            highstaff = guild.get_role(name="High Staff")
            if discordstaff in member.roles or highstaff in member.roles:
                return 1
    except: #nosec
        pass
    moderatorrole = selectquery(sql, 'guilds', 'moderator_id', f'guild_id = {guild.id}')
    roleobject = guild.get_role(moderatorrole)
    administratorrole = selectquery(sql, 'guilds', 'administrator_id', f'guild_id = {guild.id}')
    roleobject1 = guild.get_role(administratorrole)
    if await is_owner("a", member.id) == 1:
        return 1
    if roleobject in member.roles:
        return 1
    if roleobject in member.roles or roleobject1 in member.roles:
        return 1
    else:
        return 0

async def administratorcheck(guild, member): # Checks if user is a bot administrator
    if not guild:
        return 1
    administratorrole = selectquery(sql, 'guilds', 'administrator_id', f'guild_id = {guild.id}')
    roleobject = guild.get_role(administratorrole)
    if await is_owner("a", member.id) == 1:
        return 1
    if roleobject in member.roles:
        return 1
    if member.id == guild.owner_id:
        return 1
    else:
        return 0

async def statuscheck(): # Runs every 10 minutes and sends mc status to guilds
    for guild in client.guilds:
        try:
            if guild.id in premium_guilds:
                serverip = selectquery(sql, 'guilds', 'mcserver', f'guild_id = {guild.id}')
                servername = guild.name
            else:
                serverip = "play.ham5teak.xyz:25565"
                servername = "Ham5teak"
            try:
                statuschannel = selectquery(sql, 'guilds', 'statuschannel', f'guild_id = {guild.id}')
            except mysql.connector.Error as e:
                print(e)
                print(f'Failed to call statuschannel for {guild.id}')
            channel = client.get_channel(statuschannel)
            if channel is not None:
                await channel.purge(limit=10)
            if serverip is None:
                continue
            try:
                server = MinecraftServer.lookup(serverip)
                status = server.status()
                if status.latency > 0:
                    server = "Online ✅"
                else:
                    server = "Offline ❌"
                playercount = status.players.online - 20
                playercount1 = status.players.online
            except:
                server = "Offline ❌"
                playercount = 20
                playercount1 = 0
            a = await client.http.request(
                discord.http.Route(
                "GET", f"/guilds/{guild.id}")
                )
            icon = a["icon"]
            if serverip == "play.ham5teak.xyz:25565" or serverip == "play.ham5teak.xyz":
                embed = discord.Embed(description=f"**Ham5teak Status:** {server} \n**Players:** {playercount}\n**IP:** play.ham5teak.xyz\n**Versions:** 1.8.9, 1.10.x, 1.11.x, 1.12.x, 1.13.x, 1.14.x, 1.15.x, 1.16.x, 1.17.x", color=discord.Color.teal())
                embed.set_footer(text="Ham5teak Bot 3.0 | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
                embed.set_author(name="Ham5teak Network Status", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(description=f"**Status:** {server} \n**Players:** {playercount1}\n**IP:** {serverip}", color=discord.Color.teal())
                embed.set_footer(text="Ham5teak Bot 3.0 | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
                embed.set_author(name=f"{serverip.split('.', 2)[1].title()} Network Status", icon_url=f"https://cdn.discordapp.com/icons/{guild.id}/{icon}.png?size=4096")
                await channel.send(embed=embed)
        except Exception as e:
            pass
    await asyncio.sleep(600)
    
async def attachmentAutoEmbed(ctx, image:bool, type, emoji, emoji1, webhook:bool = None): # Sends embed suggestion/announcement with attachment
    await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
    file = discord.File(ctx.attachments[0].filename)
    embedDescription  = (f"{ctx.content}")
    await ctx.delete()
    if webhook == True:
        embed = addEmbed(ctx,None,embedDescription, None, False)
    else:
        embed = addEmbed(ctx,None,embedDescription)
    if image == True:
        embed.set_image(url=f"attachment://{ctx.attachments[0].filename}")
        var = "image"
    if image == False:
        var = "attachment"
    if webhook == True:
        sent = False
        sent = await sendwebhook(ctx, ctx.author.name, ctx.channel, file, [embed])
        while sent == True:
            if image != False:
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(0.5)
            msg = await ctx.channel.history(limit=1).flatten()
            msg = msg[0]
            try:
                [await msg.add_reaction(item) for item in [emoji, emoji1] if item != None]
            except:
                pass
            print(f"An {var} inclusive {type} was made in #{ctx.channel.name} by {ctx.author}.")
            os.remove(f"./{ctx.attachments[0].filename}")
            return
    else:
        msg = await ctx.channel.send(embed=embed, file=file)
    try:
        [await msg.add_reaction(item) for item in [emoji, emoji1] if item != None]
    except:
        pass
    print(f"An {var} inclusive {type} was made in #{ctx.channel.name} by {ctx.author}.")
    os.remove(f"./{ctx.attachments[0].filename}")

def addEmbed(ctx , color, new, image = None, author=True):
    if image != None and ctx != None:
        newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
        if author == True:
            newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        newEmbed.set_image(url=image)
    elif image != None and ctx == None:
        if str(color) in colors.keys():
            newEmbed = discord.Embed(description=f"{new}", color=colors[color])
        else:
            newEmbed = discord.Embed(description=f"{new}", color=color)
        newEmbed.set_image(url=image)
    else:
        if ctx != None and color == None:
            newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
            if author == True:
                newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        elif ctx != None and color != None:
            if str(color) in colors.keys():
                newEmbed = discord.Embed(description=f"{new}", color=colors[color])
            else:
                newEmbed = discord.Embed(description=f"{new}", color=color)
            if author == True:
                newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        elif ctx == None:
            if str(color) in colors.keys():
                newEmbed = discord.Embed(description=f"{new}", color=colors[color])
            else:
                newEmbed = discord.Embed(description=f"{new}", color=color)
    newEmbed.set_footer(text="Ham5teak Bot 3.0 | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
    return newEmbed

def calcshard(guildid): # Check which shard guild is in
    return (int(guildid) >> 22) % client.shard_count
