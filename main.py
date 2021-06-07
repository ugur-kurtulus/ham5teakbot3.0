import os
import aiohttp
import contextlib
import io
import textwrap
from discord.ext.commands import CommandNotFound, cooldown, BucketType
from discord.errors import HTTPException
from discord_components.select import Option
from dotenv import load_dotenv
from traceback import format_exception
from luhn import *
from cardvalidator import luhn
import random
import string
import discord
from discord.ext import commands 
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType, Select
from mcstatus import MinecraftServer
import asyncio
import emoji as e
import mysql.connector
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
host = os.getenv("mariadb_host")
port = os.getenv("mariadb_port")
database = os.getenv("mariadb_database")
username = os.getenv("mariadb_username")
password = os.getenv("mariadb_password")

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

# ------- SQL FUNCTIONS -------

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
    query = (f'DELETE FROM {database}.{table} WHERE {where}')
    print(query)
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)
            sql.commit()
            querycursor.close()
            print(f'Delete query executed successfully!')
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
    print(query)
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)  
            result = querycursor.fetchall()
            sql.commit()
            querycursor.close()
            print(f'Select query executed successfully {result}!')
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
        print(query)
    else:
        query = (f'UPDATE {database}.{table} SET {column} = {values}' + f' WHERE {where}')
        print(query)
    try:
        with sql as sql:
            querycursor = sql.cursor()
            querycursor.execute(query , values)
            sql.commit()
            querycursor.close()
            print(f'Insert query executed successfully!')
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


sql = sqlconnect()      
createtable(sql,'guilds', quilds_query)
createtable(sql,'categories', categories_query)
createtable(sql,'restrict', restrict_query)
createtable(sql,'passwords', passwords_query)

colors = {"green": 0x3aa45c, "red": 0xed4344, "blue": 0x5864f3, "aqua": 0x00FFFF,
 "dark_teal": 0x10816a, "teal": 0x1abc9c, "invis": 0x2f3037}
premium_guilds = [selectqueryall(sql, 'guilds', 'guild_id', None)]
betaannouncementguilds = []
ham_guilds = [380308776114454528, 841225582967783445, 820383461202329671,
82038346120232967, 650658756803428381, 571626209868382236, 631067371661950977]
prefixes = {}
def getprefix(client, message):
    if message.guild.id in premium_guilds and message.guild.id not in prefixes:
        pref = selectquery(sql, "guilds", "prefix", f"guild_id={message.guild.id}")
        prefixes.update({f"{message.guild.id}": f"{pref}"})
    elif message.guild.id not in premium_guilds and message.guild.id not in prefixes:
        prefixes.update({f"{message.guild.id}": f"-"})
    return commands.when_mentioned_or(*prefixes[f"{message.guild.id}"])(client, message)
client = commands.Bot(command_prefix= (getprefix))  # Defines prefix and bot
DiscordComponents(client)
slash = SlashCommand(client, sync_commands=False)  # Defines slash commands

# ------- FUNCTIONS -------

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

async def is_owner(ctx):
    return ctx.author.id == 461572795684356098 or ctx.author.id == 610930740422508544 or ctx.author == 258530967096918016

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

async def getwebhook(ctx, webhookname):
    for w in await ctx.guild.webhooks():
        if webhookname == w.name and w.channel == ctx.channel:
            return w
        
async def nopermission(ctx):
    embedDescription  = (f"You don't have permission to do this.")
    return addEmbed(ctx,None,embedDescription )

async def unknownerror(ctx, error):
    return await ctx.send(embed=addEmbed2(ctx, "red", f"`{error}`", None), delete_after=5)

async def stripmessage(string, targetstring):
    if targetstring in string:
            stringlist = string.split(f"\n")
            for stringa in stringlist:
                if targetstring in stringa:
                    return stringa

async def moderatorcheck(guild, member):
    if not guild:
        return 1
    try:
        if guild.id == 380308776114454528:
            discordstaff = guild.get_role(name="Discord Staff")
            highstaff = guild.get_role(name="High Staff")
            if discordstaff in member.roles or highstaff in member.roles:
                return 1
    except:
        pass
    moderatorrole = selectquery(sql, 'guilds', 'moderator_id', f'guild_id = {guild.id}')
    roleobject = guild.get_role(moderatorrole)
    administratorrole = selectquery(sql, 'guilds', 'administrator_id', f'guild_id = {guild.id}')
    roleobject1 = guild.get_role(administratorrole)
    if roleobject in member.roles or roleobject1 in member.roles:
        return 1
    else:
        return 0

async def administratorcheck(guild, member):
    if not guild:
        return 1
    administratorrole = selectquery(sql, 'guilds', 'administrator_id', f'guild_id = {guild.id}')
    roleobject = guild.get_role(administratorrole)
    if roleobject in member.roles:
        return 1
    else:
        return 0

async def statuscheck():
    for guild in client.guilds:
        sql.connect()
        mycursor = sql.cursor()
        guildid = int(guild.id)
        guildname = str(f"{guild.name}")
        try:
            statuschannel = selectquery(sql, 'guilds', 'statuschannel', f'guild_id = {guildid}')
        except mysql.connector.Error as e:
            print(e)
            print(f'Failed to call statuschannel for {guildid}')
            return
        mycursor.close()
        try:
            channel = client.get_channel(statuschannel)
            await channel.purge(limit=10)
            server = MinecraftServer.lookup("play.ham5teak.xyz:25565")
            status = server.status()
            if status.latency >= 0.0001:
                ham5teak = "Online ✅"
            else:
                ham5teak = "Offline ❌"
            embed = discord.Embed(description=f"**Ham5teak Status:** {ham5teak} \n**Players:** {status.players.online - 20}\n**IP:** play.ham5teak.xyz\n**Versions:** 1.13.x, 1.14.x, 1.15.x, 1.16.x", color=discord.Color.teal())
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
            embed.set_author(name="Ham5teak Network Status", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
            await channel.send(embed=embed)
        except:
            pass
    await asyncio.sleep(600)
    
async def attachmentAutoEmbed(ctx, image:bool, type, emoji, emoji1, webhook:bool = None):
    await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
    file = discord.File(ctx.attachments[0].filename)
    embedDescription  = (f"{ctx.content}")
    await ctx.delete()
    if webhook != None and webhook == True:
        embed = addEmbed2(ctx,None,embedDescription)
    else:
        embed = addEmbed(ctx,None,embedDescription)
    if image == True:
        embed.set_image(url=f"attachment://{ctx.attachments[0].filename}")
        var = "image"
    if image == False:
        var = "attachment"
    if webhook != None and webhook == True:
        sent = False
        sent = await sendwebhook(ctx, ctx.author.name, ctx.channel, file, [embed])
        while sent == True:
            msg = await ctx.channel.history(limit=1).flatten()
            msg = msg[0]
            await msg.add_reaction(emoji)
            await msg.add_reaction(emoji1)
            print(f"An {var} inclusive {type} was made in #{ctx.channel.name} by {ctx.author}.")
            os.remove(f"./{ctx.attachments[0].filename}")
            return
    else:
        msg = await ctx.channel.send(embed=embed, file=file)
    await msg.add_reaction(emoji)
    await msg.add_reaction(emoji1)
    print(f"An {var} inclusive {type} was made in #{ctx.channel.name} by {ctx.author}.")
    os.remove(f"./{ctx.attachments[0].filename}")
    
def addEmbed2(ctx , color, new, image = None):
    if image != None and ctx != None:
        newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
        newEmbed.set_image(url=image)
    elif image != None and ctx == None:
        newEmbed = discord.Embed(description=f"{new}", color=colors[color])
        newEmbed.set_image(url=image)
    else:
        if ctx != None and color == None:
            newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
        elif ctx != None and color != None:
            newEmbed = discord.Embed(description=f"{new}", color=colors[color])
        elif ctx == None:
            newEmbed = discord.Embed(description=f"{new}", color=colors[color])
    newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
    return newEmbed

def addEmbed(ctx , color, new, image = None):
    if image != None and ctx != None:
        newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
        newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        newEmbed.set_image(url=image)
    elif image != None and ctx == None:
        newEmbed = discord.Embed(description=f"{new}", color=colors[color])
        newEmbed.set_image(url=image)
    else:
        if ctx != None and color == None:
            newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
            newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        elif ctx != None and color != None:
            newEmbed = discord.Embed(description=f"{new}", color=colors[color])
        elif ctx == None:
            newEmbed = discord.Embed(description=f"{new}", color=colors[color])
    newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
    return newEmbed

# ------- STARTUP EVENT -------

@client.event
async def on_ready():
    print("""\
╭╮ ╭╮     ╭━━━┳╮      ╭╮    ╭━━╮   ╭╮   ╭━━━╮   ╭━━━╮
┃┃ ┃┃     ┃╭━┳╯╰╮     ┃┃    ┃╭╮┃  ╭╯╰╮  ┃╭━╮┃   ┃╭━╮┃
┃╰━╯┣━━┳╮╭┫╰━┻╮╭╋━━┳━━┫┃╭╮  ┃╰╯╰┳━┻╮╭╯  ╰╯╭╯┃   ┃┃┃┃┃
┃╭━╮┃╭╮┃╰╯┣━━╮┃┃┃┃━┫╭╮┃╰╯╯  ┃╭━╮┃╭╮┃┃   ╭╮╰╮┃   ┃┃┃┃┃
┃┃ ┃┃╭╮┃┃┃┣━━╯┃╰┫┃━┫╭╮┃╭╮╮  ┃╰━╯┃╰╯┃╰╮  ┃╰━╯┣ ╭╮┃╰━╯┃
╰╯ ╰┻╯╰┻┻┻┻━━━┻━┻━━┻╯╰┻╯╰╯  ╰━━━┻━━┻━╯  ╰━━━┻ ╰╯╰━━━╯
                   """)
    sql.connect()
    quildcursor = sql.cursor()
    quildcursor.execute("SELECT guild_id FROM guilds")  
    for row in quildcursor.fetchall(): 
        premium_guilds.append(row[0])
    quildcursor.close()
    print('Logged on as {0}!'.format(client.user.name))
    activity = discord.Game(name="play.ham5teak.xyz")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print("Presence has been set!")
    message = ""
    for guild in client.guilds:
        message += f"{guild.name}\n"
    embedDescription  = (f"**__Guilds:__ **\n{message}")
    channel = client.get_channel(841245744421273620)
    await channel.send(embed=addEmbed(None, "teal", embedDescription))
    #client.load_extension('music')
    client.remove_command('help')
    result = selectqueryall(sql, 'guilds', 'guild_id', 'betaannouncements = 1')
    for type in result:
        type1 = type[0]
        betaannouncementguilds.append(type1)
    while True:
        await statuscheck()

# ------- CLIENT COMMANDS -------

@client.command()
@commands.has_permissions(manage_guild=True)
@commands.guild_only()
async def setprefix(ctx, prefix = None):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    if prefix is None:
        embedDescription  = (f"Please provide all required arguments. `-setprefix <prefix>`.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return
    if len(prefix) >= 6:
        embedDescription  = (f"{prefix} has too many characters for a prefix.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return
    if ctx.guild.id in premium_guilds:
        insertquery(sql, "guilds", "prefix", f"'{prefix}'", f"guild_id = {ctx.guild.id}")
        prefixes[f"{ctx.guild.id}"] = prefix
    elif ctx.guild.id not in premium_guilds:
        prefixes[f"{ctx.guild.id}"] = prefix
    else: 
        return
    embedDescription  = (f"Prefix succesfully set to `{prefix}`")
    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)

@client.command()
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send(embed=addEmbed(ctx, "dark_teal", f"Bot Latency: `{client.latency}ms`"), delete_after=5)

@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount:int):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)
    embedDescription  = (f"{amount} messages were successfully deleted.")
    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=1)

@client.command()
@discord.ext.commands.has_guild_permissions(manage_guild=True)
@commands.cooldown(1, 15, commands.BucketType.user)
async def setup(ctx, password, admin_role_id:discord.Role, mod_role_id:discord.Role):
    await ctx.message.delete()
    async def invalidpass():
        embedDescription  = (f"Invalid password.")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), delete_after=5)
    cc = password[:16]
    password = password[16:].strip()
    if verify(cc) == False:
        print("cc fail")
        await invalidpass()
        return
    elif verify(cc) == True:
        check = selectqueryall(sql, f'passwords', 'password', None)
        found = False
        for pass1 in check:
            if pass1[0] == password:
                found = True
        if found != True:
            print("pass doesn't exist")
            await invalidpass()
            return
        check2 = selectquery(sql, f'passwords', 'used', f"password = '{password}'")
        if check2 == 1:
            embedDescription  = (f"This password was already used.")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
            return
        elif check2 == 0:
            insertquery(sql, f'passwords', 'used', '(1)', f'password = "{str(password)}"')
            insertquery(sql, f'passwords', 'guild_id', f'{ctx.guild.id}', f'password = "{str(password)}"')
    guild_id = ctx.guild.id
    if guild_id in premium_guilds:
        embedDescription  = (f"You are already Logged in as Premium")
        await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ))
        return
    else:
        guild_name = ctx.guild.name
        column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
        values = (guild_id , guild_name , True , admin_role_id.id , mod_role_id.id)
        where = None
        result = (insertquery(sql, 'guilds' , column , values, where))
        premium_guilds.append(ctx.guild.id)
        if result == 0:
            embedDescription  = (f"Registered successfully")
            await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
        else:
            embedDescription  = (f"Register Failed")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)

@client.command()
@discord.ext.commands.has_guild_permissions(manage_guild=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def generate(ctx):
    if ctx.channel != client.get_channel(850260644322344960):
        return
    password = ''
    stringpunc = string.punctuation.replace("'", "").replace('"', '').replace('`', '')
    await ctx.message.delete()
    for x in range (0,4):
        Password = random.choice(string.digits)
    for y in range(8):
        password = password + random.choice(string.digits)
    check = selectqueryall(sql, f'passwords', 'password', None)
    for pass1 in check:
        if pass1 == password:
            return await generate(ctx)
    result = insertquery(sql, f'passwords', '(password, used)', (password, 0), None)
    if result != 1:
        cc = luhn.generate(16)
        embedDescription  = (f"**Generated Password:** `{cc}{password}`")
    else:
        embedDescription  = (f"Password generation failed.")
    await ctx.send(embed=addEmbed(None, "aqua", embedDescription))

@client.command()
@discord.ext.commands.has_guild_permissions(manage_guild=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def setrestrict(ctx, alias ,role1:discord.Role, role2:discord.Role = None, role3:discord.Role = None):
    await ctx.message.delete()
    guild_id = ctx.guild.id
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    if guild_id not in premium_guilds:
        embedDescription  = (f"You premium to use this command.")
        await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ), delete_after=5)
        return
    restricttypes = selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')
    for stralias in restricttypes:
        if alias == stralias[0]:
            embedDescription  =(f"Restrict type `{alias}` already exists.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return 1
    else:
        if role3 is None:
            if role2 is None:
                column = '(guild_id  , restrictrole_name , restrictrole_id)'
                values = (guild_id , alias , role1.id)
                where = None
                result = (insertquery(sql, f'restrict' , column , values, where))
                sql.connect()
                querycursor = sql.cursor()
                sql.commit()
                querycursor.close()        
                if (result == 0):
                    embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention}")
                    await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
                else:
                    embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention}")
                    await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return
            column = '(guild_id  , restrictrole_name , restrictrole_id , restrictrole2_id)'
            values = (guild_id , alias , role1.id , role2.id)
            where = None
            result = (insertquery(sql, f'restrict' , column , values, where))
            sql.connect()
            querycursor = sql.cursor()
            sql.commit()
            querycursor.close()        
            if (result == 0):
                embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention} and {role2.mention}")
                await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
            else:
                embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention} and {role2.mention}")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return
        column = '(guild_id  , restrictrole_name , restrictrole_id , restrictrole2_id, restrictrole3_id)'
        values = (guild_id , alias , role1.id , role2.id, role3.id)
        where = None
        result = (insertquery(sql, f'restrict' , column , values, where))
        sql.connect()
        querycursor = sql.cursor()
        sql.commit()
        querycursor.close()        
        if (result == 0):
            embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention}, {role2.mention} and {role3.mention}")
            await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
        else:
            embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention}, {role2.mention} and {role3.mention}")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return

@client.command()
async def edit(ctx, id, *, embedDescription):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    msg = await ctx.channel.fetch_message(id)
    embedobj = msg.embeds[0]
    if msg.author.id != client.user.id:
        await ctx.message.delete()
        webhook1 = await getwebhook(ctx, "Ham5teakBot3")
        async with aiohttp.ClientSession() as session:
            webh = discord.Webhook.from_url(webhook1.url, adapter=discord.AsyncWebhookAdapter(session=session))
            await webh.edit_message(id, embeds=[addEmbed2(ctx, None, embedDescription, embedobj.image.url)])
        return
    await ctx.message.delete()
    await ctx.channel.get_partial_message(id).edit(embed = addEmbed(ctx, None, embedDescription, embedobj.image.url))

@client.command()
@commands.guild_only()
async def prefix(ctx):
    await ctx.message.delete()
    prefix = prefixes[f"{ctx.guild.id}"]
    await ctx.send(embed=addEmbed(ctx, None, f"Bot Prefix: `{prefix}`"), delete_after=5)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def setchannel(ctx, command, channel: discord.TextChannel):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    guild_id = ctx.guild.id
    channelid = str(channel.id)
    commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
    , "rejectedsuggestions", "acceptedsuggestions", "demandedsuggestions"]
    for commanda in commandsloop:
        if commanda == command:
            column = (command)
            values = (channelid)
            where = (f"guild_id = {guild_id}")
            result = (insertquery(sql, 'guilds', column , values, where))
            if (result == 0):
                embedDescription  = (f"Successfully registered {command} as `{channel.id}`")
                await ctx.channel.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
            else:
                embedDescription  = (f"Couldn't register {command} as {channelid}")
                await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)     

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def move(ctx, alias):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    aliaslist = selectqueryall(sql, "categories", "category_name", f"guild_id = {ctx.guild.id}")
    for stralias in aliaslist:
        if alias == stralias[0]:
            ctxchannel = ctx.channel
            result = selectquery(sql, "categories", "category_id", f"category_name = '{alias}' AND guild_id = {ctx.guild.id}")
            cat = client.get_channel(result)
            await ctxchannel.edit(category=cat)
            embedDescription  = (f"{ctxchannel.mention} has been moved to category {alias}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)

@client.command(aliases=['rl'])
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def restrictlist(ctx):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    types = [selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')]
    for type in types:
        if types == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        type1 = str(type).replace('(', '').replace(')', '').replace('(', '').replace("'", '').replace("[", '').replace("]", '').replace(',', '').replace(' ', f'\n')
        embedDescription  = (f"__**Restriction types you can use:**__\n{type1}")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), delete_after=10)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def restrict(ctx, alias):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    if alias.lower() == "none":
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)
        embedDescription  = (f"{ctx.channel.mention} has been opened to public.")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
    aliaslist = selectqueryall(sql, f"restrict", "restrictrole_name", f"guild_id = {ctx.guild.id}")
    for stralias in aliaslist:
        if alias == stralias[0]:
            ctxchannel = ctx.channel
            sql.connect()
            result = selectquery(sql, f"restrict", "restrictrole3_id", f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
            if result is None:
                result1 = selectquery(sql, f'restrict', 'restrictrole2_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                if result1 is None:
                    result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                    role = ctx.guild.get_role(result2)
                    overwrites1= {}
                    overwrites1.update({role: discord.PermissionOverwrite(view_channel=True),
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
                    await ctx.channel.edit(overwrites=overwrites1)
                    embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention}")
                    await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
                    return
                result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                cat = ctx.guild.get_role(result1)
                cat2 = ctx.guild.get_role(result2)
                overwrites2 = {}
                overwrites2.update({cat: discord.PermissionOverwrite(view_channel=True), cat2: discord.PermissionOverwrite(view_channel=True),
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
                await ctx.channel.edit(overwrites=overwrites2)
                embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention} and {cat2.mention}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
                return
            result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
            result3 = selectquery(sql, f'restrict', 'restrictrole2_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
            cat = ctx.guild.get_role(result)
            cat2 = ctx.guild.get_role(result2)
            cat3 = ctx.guild.get_role(result3)
            overwrites3 = {}
            overwrites3.update({cat: discord.PermissionOverwrite(view_channel=True), cat2: discord.PermissionOverwrite(view_channel=True),
            cat3: discord.PermissionOverwrite(view_channel=True), ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
            await ctx.channel.edit(overwrites=overwrites3)
            embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention}, {cat2.mention} and {cat3.mention}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def setmove(ctx, categoryi: discord.CategoryChannel, alias):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    movecheck = selectquery(sql, 'guilds', 'custommovecount', f'guild_id = {ctx.guild.id}')
    if movecheck >= 45:
        await ctx.send(embed=addEmbed(ctx, None, f"Guild has {movecheck} custommoves set which is over the limit."), delete_after=5)
        return
    await ctx.message.delete()
    guild_id = ctx.guild.id
    categoryid = str(categoryi.id)
    categoryname = str(alias).replace('"', '').replace("'", "")
    if guild_id not in premium_guilds:
        embedDescription  = (f"You need premium to use this command.")
        await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ))
        return
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            embedDescription  =(f"Category `{categoryname}` already exists.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return 1
    column = '(guild_id, category_name)'
    values = (guild_id, categoryname)
    where = None
    result = (insertquery(sql, 'categories', column , values, where))
    column = ('category_id')
    values = (f"'{categoryid}'")
    where = (f"category_name = '{categoryname}'")
    result = (insertquery(sql, 'categories', column , values, where))
    if (result == 0):
        embedDescription =(f"Successfully registered {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
        insertquery(sql, 'guilds', 'custommovecount', f'{len(categoryn) + 1}', f'guild_id = {ctx.guild.id}')
    else:
        embedDescription  =(f"Couldn't register {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def removerestrict(ctx, alias):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    restrictname = alias
    restrictlist = selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')
    for stralias in restrictlist:
        if restrictname == stralias[0]:
            deletequery(sql, f'restrict', f"restrictrole_name = '{restrictname}'")
            embedDescription  =(f"Restriction type `{restrictname}` has been removed.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return 1
    embedDescription  =(f"Restriction type `{restrictname}` couldn't be removed.")
    await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
    return 1

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def removemove(ctx, alias):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    categoryname = alias
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            categoryn = deletequery(sql, 'categories', f"category_name = '{categoryname}'")
            embedDescription  =(f"Category `{categoryname}` has been removed.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return 1
    embedDescription  =(f"Category `{categoryname}` couldn't be removed.")
    await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
    return 1

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def demanded(ctx, messageid):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    result = selectquery(sql, 'guilds', 'demandedsuggestions', f'guild_id = {ctx.guild.id}')
    if result == 0:
        embedDescription  = (f"This server doesn't have a demanded suggestions channel set.")
        await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), delete_after=5)
    else:
        msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
        for reaction in msg.reactions:
            if reaction.emoji != "✅":
                pass 
            else:
                reactiona = reaction
                dsuggestionschannel = client.get_channel(result)
                finalcount = int(reactiona.count - 1)
                embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                embed2 = msg.embeds[0]
                await sendwebhook(ctx, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully demanded!")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
                return

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def reject(ctx, messageid):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    result = selectquery(sql, 'guilds', 'rejectedsuggestions', f'guild_id = {ctx.guild.id}')
    if result == 0:
        embedDescription  = (f"This server doesn't have a rejected suggestions channel set.")
        await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), delete_after=5)
    else:
        msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
        for reaction in msg.reactions:
            if reaction.emoji != "❌":
                pass
            else:
                reactiona = reaction
                rsuggestionschannel = client.get_channel(result)
                finalcount = int(reactiona.count - 1)
                embedDescription  = (f"**{finalcount} Downvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                embed2 = msg.embeds[0]
                await sendwebhook(ctx, "Rejected Suggestions", rsuggestionschannel, None, [embed1, embed2])
                embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully rejected!")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
                return
    
@client.command(aliases=['scc'])
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def simchannelcreate(ctx):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.message.delete()
    await on_guild_channel_create(ctx.channel)

@client.command(aliases=['ml'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def movelist(ctx):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5) 
        return
    await ctx.message.delete()
    categories = [selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')]
    for category in categories:
        if categories == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        newcat = str(category).replace('(', '').replace(')', '').replace('(', '').replace("'", '').replace("[", '').replace("]", '').replace(',', '').replace(' ', f'\n')
        embedDescription  = (f"__**Categories you can move channels to:**__\n{newcat}")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=10)   

@client.command(aliases=['eval', 'e'])
@commands.check(is_owner)
async def evaluate(ctx, *, code):
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": client,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )

            obj = await local_variables["func"]()
            if obj is not None:
                result = f"{stdout.getvalue()}\n-- {obj}\n"
            else:
                result = f"{stdout.getvalue()}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))
   	
    await ctx.send(embed=addEmbed(ctx, "invis", f"```py\n{result}\n```"))
        
@client.command(aliases=['ba'])
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def betaannouncements(ctx, bool:bool):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5) 
        return
    await ctx.message.delete()
    if bool == True:
        insertquery(sql, 'guilds', 'betaannouncements', ('1'), f'guild_id = {ctx.guild.id}')
        betaannouncementguilds.append(ctx.guild.id)
    if bool == False:
        insertquery(sql, 'guilds', 'betaannouncements', ('0'), f'guild_id = {ctx.guild.id}')
        betaannouncementguilds.remove(ctx.guild.id)
    embedDescription  = (f"Beta-Announcements have successfully been set to `{bool}`.")
    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5) 

# ------- ERROR HANDLERS -------

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.errors.CommandNotFound):
        return
    print(error)

@evaluate.error
async def clear_error(ctx, error):
    await ctx.send(embed=addEmbed2(ctx, "invis", f'```py\n{error}\n```'))

@move.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter the command correctly. `{getprefix2(ctx)}move <category>`'), delete_after=5)
    elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category. `{getprefix2(ctx)}move <category>`'), delete_after=5)
    else:
        await unknownerror(ctx, error)

@ping.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)

@betaannouncements.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)
    
@movelist.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)
    
@restrictlist.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)
    
@setup.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)
    
@removerestrict.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)
    
@generate.error
async def clear_error(ctx, error):
    await unknownerror(ctx, error)

@setmove.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.ChannelNotFound):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category id. `{getprefix2(ctx)}setmove <categoryid> <alias>`'), delete_after=5)
    else:
        await unknownerror(ctx, error)
        
@removemove.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category name. `{getprefix2(ctx)}removemove <categoryname>`'), delete_after=5)
    else:
        await unknownerror(ctx, error)

@edit.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the id of the message you would like to edit. `{getprefix2(ctx)}edit <messageid> <newmessage>`'), delete_after=5)
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(embed=addEmbed2(ctx, "red", 'Please enter a valid message ID.', None), delete_after=5)
    else:
        await unknownerror(ctx, error)

@setchannel.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the channel you would like to set. `{getprefix2(ctx)}setchannel <channel> <id>`', None), delete_after=5)
    else:
        await unknownerror(ctx, error)

@purge.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.message.delete()
        await ctx.send(embed=addEmbed2(ctx, "red", f'Please make sure to enter a number. `{getprefix2(ctx)}purge <amount>`', None), delete_after=5)
    else:
        await unknownerror(ctx, error)

@restrict.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the restrict type you would like to apply. `{getprefix2(ctx)}restrict <type>`', None), delete_after=5)
    else:
        await unknownerror(ctx, error)

@setrestrict.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please make sure to give all arguments correctly. `{getprefix2(ctx)}setrestrict <type> <role1> [role2] [role3]`', None), delete_after=5)
    else:
        await unknownerror(ctx, error)
    
@setprefix.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send(f'Please specify the prefix you would like to apply. `{getprefix2(ctx)}setprefix <prefix>`', delete_after=5)
    else:
        await unknownerror(ctx, error)

# ------- SLASH COMMANDS -------
    
@slash.slash(name="accept")
async def accept(ctx, messageid):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.defer(hidden=True)
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    result = selectquery(sql, 'guilds', 'acceptedsuggestions', f'guild_id = {ctx.guild.id}')
    if result == 0:
        embedDescription  = (f"This server doesn't have an accepted suggestions channel set.")
        await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), hidden=True)
    else:
        msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
        for reaction in msg.reactions:
            if reaction.emoji != "✅":
                return 
            else:
                await ctx.defer(hidden=True)
                reactiona = reaction
                aschannel = client.get_channel(result)
                finalcount = int(reactiona.count - 1)
                embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                embed2 = msg.embeds[0]
                await sendwebhook(ctx, "Accepted Suggestions", aschannel, None, [embed1, embed2])
                embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully accepted!")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
                return

@slash.slash(name="ham5teak", description="View Ham5teak network status")
async def ham5teak(ctx):
    server = MinecraftServer.lookup("play.ham5teak.xyz:25565")
    status = server.status()
    if status.latency >= 0.0001:
        ham5teak = "Online ✅"
    else:
        ham5teak = "Offline ❌"
    embedDescription =(f"**Ham5teak Status:** {ham5teak} \n**Players:** {status.players.online - 20}")
    await ctx.send(embed=addEmbed(ctx,None,embedDescription ))  

@slash.slash(name="help")
async def help(ctx):
    await ctx.defer(hidden=True)
    await ctx.send("boo")

@slash.slash(name="move", description="Move a channel to specified category.", )
async def move(ctx, category):
    await ctx.defer(hidden=True)
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    alias = category
    aliaslist = selectqueryall(sql, "categories", "category_name", f"guild_id = {ctx.guild.id}")
    for stralias in aliaslist:
        if alias == stralias[0]:
            ctxchannel = ctx.channel
            result = selectquery(sql, "categories", "category_id", f"category_name = '{alias}' AND guild_id = {ctx.guild.id}")
            cat = client.get_channel(result)
            await ctxchannel.edit(category=cat)
            embedDescription  = (f"{ctxchannel.mention} has been moved to category {alias}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ))

@slash.slash(name="tag", description="A command used to leave a note to a channel")
async def tag(ctx, note, user:discord.User = None, channel:discord.TextChannel = None, role:discord.Role = None):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        await ctx.defer(hidden=True)
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    await ctx.defer(hidden=False)
    finalmentions = []
    mentions = [user, channel, role]
    for mention in mentions:
        if mention is not None:
            if finalmentions == 0:
                finalmentions.insert(mention.mention)
            finalmentions.append(mention.mention)
    for mention in mentions:
        if mention is not None:
            embedDescription =(f"{ctx.author.mention} has tagged the channel as `{note.upper()}` \n\n**Mentions:** {', '.join(finalmentions)}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ))
            return
    embedDescription  = (f"{ctx.author.mention} has tagged the channel as `{note.upper()}`")
    await ctx.send(embed=addEmbed(ctx,None,embedDescription )) 

# ------- SETTING SLASH COMMANDS -------

@slash.slash(name="setchannel", description="Set channels for your server")
@commands.has_permissions(manage_guild=True)
async def setchannel(ctx, value: discord.TextChannel, channel):
    await ctx.defer(hidden=True)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    guild_id = ctx.guild.id
    channelid = str(value.id)
    commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
    , "acceptedsuggestions", "rejectedsuggestions", "demandedsuggestions"]
    for commanda in commandsloop:
        if commanda == channel:
            column = (channel)
            values = (channelid)
            where = (f"guild_id = {guild_id}")
            result = (insertquery(sql, 'guilds', column , values, where))
            if result is not None:
                embedDescription  = (f"{channel} successfully registered as <#{channelid}>")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
            else:
                embedDescription  = (f"{channel} couldn't be registered as {channelid}")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))  
        
@slash.slash(name="setmove")
@commands.has_permissions(manage_guild=True)
async def setmove(ctx, categoryi: discord.CategoryChannel, alias):
    await ctx.defer(hidden=True)
    await administratorcheck(ctx.guild, ctx.author)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    movecheck = selectquery(sql, 'guilds', 'custommovecount', f'guild_id = {ctx.guild.id}')
    if movecheck >= 45:
        await ctx.send(embed=addEmbed(ctx, None, f"Guild has {movecheck} custommoves set which is over the limit."), delete_after=5)
        return
    guild_id = ctx.guild.id
    categoryid = str(categoryi.id)
    categoryname = str(alias).replace('"', '').replace("'", "")
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            embedDescription  =(f"Category `{categoryname}` already exists.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))
            return 1
    column = '(guild_id, category_name)'
    values = (guild_id, categoryname)
    where = None
    result = (insertquery(sql, 'categories', column , values, where))
    column = ('category_id')
    values = (categoryid)
    where = (f"category_name = '{categoryname}'")
    result = (insertquery(sql, 'categories', column , values, where))
    if (result == 0):
        embedDescription =(f"Successfully registered {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ))   
        insertquery(sql, 'guilds', 'custommovecount', f'{len(categoryn) + 1}', f'guild_id = {ctx.guild.id}')
    else:
        embedDescription  =(f"Couldn't register {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))

@slash.slash(name="setrole")
@commands.has_permissions(manage_guild=True)
async def setrole(ctx, administrator:discord.Role, moderator: discord.Role):
    await ctx.defer(hidden=True)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        await ctx.send(embed=await nopermission(ctx), delete_after=5)
        return
    result = selectquery(sql, 'guilds', 'moderator_id', f'guild_id = {ctx.guild.id}')
    if result is None:
        embedDescription  = (f"Server needs to be setup before executing this command.")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ))
    elif result is not None:
        a = insertquery(sql, "guilds", "moderator_id", f"{moderator.id}", f"guild_id = {ctx.guild.id}")
        b = insertquery(sql, "guilds", "administrator_id", f"{administrator.id}", f"guild_id = {ctx.guild.id}")
        if (a == 0) and (b == 0):
            embedDescription  = (f"New administrator and moderator roles have successfully been set as {administrator.mention} {moderator.mention}")
            await ctx.send(embed=addEmbed(ctx,"green",embedDescription ))
        else:
            embedDescription  = (f"Couldn't register {administrator.mention} {moderator.mention} as administrator and moderator.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))

@slash.slash(name="setup")
@commands.has_permissions(manage_guild=True)
async def setup(ctx, password, administrator:discord.Role, moderator:discord.Role):
    await ctx.defer(hidden=True)
    async def invalidpass():
        embedDescription  = (f"Invalid password.")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription))
    cc = password[:16]
    password = password[16:].strip()
    if verify(cc) == False:
        await invalidpass()
        return
    elif verify(cc) == True:
        check = selectqueryall(sql, f'passwords', 'password', None)
        for pass1 in check:
            if pass1[0] != password:
                found = False
            if pass1[0] == password:
                found = True
        if found != True:
            await invalidpass()
            return
        check2 = selectquery(sql, f'passwords', 'used', f"password = '{password}'")
        if check2 == 1:
            embedDescription  = (f"This password was already used.")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
            return
        elif check2 == 0:
            insertquery(sql, f'passwords', 'used', '(1)', f'password = "{str(password)}"')
            insertquery(sql, f'passwords', 'guild_id', f'{ctx.guild.id}', f'password = "{str(password)}"')
    guild_id = ctx.guild.id
    if guild_id in premium_guilds:
        embedDescription  = (f"You are already logged in as Premium.")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
        return
    else:
        guild_name = ctx.guild.name
        column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
        values = (guild_id , guild_name , True , administrator.id , moderator.id)
        where = None
        insertquery(sql, 'guilds' , column , values, where)
        insertcheck = selectquery(sql, 'guilds', 'premium', f'guild_id = {ctx.guild.id}')   
        premium_guilds.append(ctx.guild.id) 
        if insertcheck != 0:
            embedDescription  = (f"Setup successfully completed!")
            await ctx.send(embed=addEmbed(ctx,"green",embedDescription ))
        else:
            embedDescription  = (f"Setup failed!")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))

# ------- SLASH COMMAND ERROR HANDLERS -------
@client.event
async def on_slash_command_error(ctx, error):
    print(error)
    if isinstance(error, discord.errors.NotFound):
        embedDescription  = (f"Please enter a valid ID. \n{error}")
        await ctx.send(embed=addEmbed(ctx,"teal",embedDescription ), hidden=True)
    if isinstance(error, commands.MissingPermissions):
        await ctx.defer(hidden=True)
        embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
    if isinstance(error, commands.ChannelNotFound):
        await ctx.defer(hidden=True)
        embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
    if isinstance(error, commands.RoleNotFound):
        await ctx.defer(hidden=True)
        embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
    if isinstance(error, commands.MemberNotFound):
        await ctx.defer(hidden=True)
        embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
    else:
        await ctx.send(embed=addEmbed2(ctx, "red", f"Unknown error: {error}", None), hidden=True)

# ------- EVENT HANDLERS -------

@client.event
async def on_guild_channel_create(channel):
    if "ticket-" not in channel.name:
        return
    if channel.guild.id not in ham_guilds:
        return

    embedDescription  = f"""Hello! The staff team will be assisting you shortly.
In order to make this process easier for us staff, please choose from
the following choices by clicking the button describing your issue.

1. **Item Lost** 
2. **Reporting an Issue/Bug**
3. **Same IP Connection** 
4. **Connection Problems**
5. **Discord Issue**
6. **Forgot Password**
7. **Ban/Mute Appeal**
8. **Queries**
9. **In-Game Rank Parity**
10. **Role Application**"""

    async def embed1(embedDescription):
        embed1 = discord.Embed(description=f"{embedDescription}", color=discord.Color.dark_teal())
        embed1.set_author(name="Ham5teak Bot Ticket Assistant", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
        embed1.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
        return embed1
    
    if channel.guild.id == 380308776114454528:
        content1 = "<@&832198461495443506>"
    else:
        content1 = None
    msg = await channel.send(content=content1, embed=await embed1(embedDescription),components=[
                # Row 1
                [Button(style=ButtonStyle.green, label=f"1", id="Item Lost"),
                Button(style=ButtonStyle.green, label=f"2", id="Issue or Bug Report"),
                Button(style=ButtonStyle.green, label=f"3", id="Same IP Connection"),
                Button(style=ButtonStyle.green, label=f"4", id="Connection Problems"),
                Button(style=ButtonStyle.green, label=f"5", id="Discord Issue")],
                # Row 2
                [Button(style=ButtonStyle.green, label=f"6", id="Forgot Password"),
                Button(style=ButtonStyle.green, label=f"7", id="Ban or Mute Appeal"),
                Button(style=ButtonStyle.green, label=f"8", id="Queries"),
                Button(style=ButtonStyle.green, label=f"9", id="In-Game Rank Parity"),
                Button(style=ButtonStyle.green, label=f"10", id="Role Application"),],
                # Row 3
                [Button(style=ButtonStyle.URL, label=f"Visit Store", url="http://shop.ham5teak.xyz/"),
                Button(style=ButtonStyle.URL, label=f"Visit Forums", url="https://ham5teak.xyz/")],
                ])
    while True:
        res = await client.wait_for(event="button_click",check=lambda res: res.channel == channel)
        if res.component.id == "Item Lost":
            embedDescription1 = f"1. **Item Lost Due To Server Lag/Crash** \n\n\`\`\`\nIn-game Name:\nServer:\nItems you lost:  \n\`\`\`\n\nIf they are enchanted tools, please mention the enchantments if possible."
        elif res.component.id == "Issue or Bug Report":
            embedDescription1 = f"2. **Issue/Bug Report** \n\n\`\`\`\nIn-Game Name : \nServer: \nIssue/Bug :\n\`\`\`"
        elif res.component.id == "Same IP Connection":
            embedDescription1 = f"3. **Same IP Connection** \n\n\`\`\`\nIn-Game Name of Same IP Connection : \n- \n- \n\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
        elif res.component.id == "Connection Problems":
            embedDescription1 = f"4. **Connection Problems** \n\n\`\`\`\nIn-game Name:\nWhat connection problem are you facing? Please explain briefly:\n\`\`\`\n\n"
        elif res.component.id == "Discord Issue":
            embedDescription1 = f"5. **Discord Issue** \nPlease state your issue and wait patiently until our support team arrives."
        elif res.component.id == "Forgot Password":
            embedDescription1 = f"6. **Forgot Password** \n\n\`\`\`\nIn-game Name:\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
        elif res.component.id == "Ban or Mute Appeal":
            embedDescription1 = f"""7. **Ban/Mute Appeal** \n\n\`\`\`\nWhy did you get banned/muted? \nWas it on discord or in-game?\n\`\`\` \nIf it was in-game, what is your in-game name and who banned/muted you? 
        \nAlso - please do a ban appeal/mute appeal next time using https://ham5teak.xyz/forums/ban-appeal.21/"""
        elif res.component.id == "Queries":
            embedDescription1 = f"""8. **Queries** \nPlease state your questions here and wait patiently for a staff to reply.\nIf you have to do something at the moment, please leave a note for Staff."""
        elif res.component.id == "In-Game Rank Parity":
            embedDescription1 = f"""9. **In-Game Rank Parity** \nPlease state your In-Game Name and rank you would like to be paired.\nIf you have to do something at the moment, please leave a note for Staff.
            \n\`\`\`\nIn-Game Name: \nRank: \n\`\`\`\n"""
        elif res.component.id == "Role Application":
            embedDescription1 = f"""10. **Role Application** \nPlease state the role you want to apply for `Youtuber/DJ/Dev-Chat`.
            \nIf you're applying for youtuber please send a video you've recorded in Ham5teak if not please wait until our support team arrives."""
        if embedDescription1 is not None:
            await msg.edit(embed=await embed1(embedDescription1),components=[
            Button(style=ButtonStyle.green, label=f"{res.user} chose {res.component.id}", disabled=True)
            ]) 
        serversandcats = {
        "Survival": 632946682207928321, "Skyblocks": 632946712805244948, "Semi-Vanilla": 667988805059346435, 
        "Factions": 659020993553104896, "Prison": 632946839792123948, "Creative": 632946812092678154, 
        "Caveblocks": 786399045081890858, "Minigames": 664805277991960586
        }
        options1 = []
        for server in serversandcats.keys():
            options1.append(Option(label=server, value=server))
        await res.respond(
            type=InteractionType.ChannelMessageWithSource,
            embed= await embed1(f"""{res.component.id} chosen."""),
            components=[Select(id=f"{res.component.id}-{res.user.name}",options=options1, placeholder="Choose A Server"
        )])
        if "ticket-" in channel.name:
            await channel.edit(name=f"{res.component.id}-{res.user.name}")
        if channel.guild.id not in ham_guilds:
            return
        serversent = True
        while serversent == True:
            res1 = await client.wait_for("select_option", check=lambda res1: res1.component["custom_id"].replace(" ", "-").lower() == channel.name)
            for servername in serversandcats.keys():
                if res1.component["values"][0] == servername:
                    cat = client.get_channel(serversandcats[servername])
                    await channel.edit(category=cat)
            embedDescription2 = f"{res1.component['values'][0]} selected as ticket category."
            await res1.respond(
                type=InteractionType.UpdateMessage,
                embed=await embed1(embedDescription2),
                components=[]
            )
            serversent = False


@client.event
async def on_reaction_add(reaction, user):
    messageid = reaction.message.id
    rcount = 8
    if "suggestions" in reaction.message.channel.name and "staff-suggestions" not in reaction.message.channel.name:
        if reaction.emoji == "✅":
            if reaction.count == rcount:
                dsuggestions = selectquery(sql, 'guilds', 'demandedsuggestions', f'guild_id = {reaction.message.guild.id}')
                channel = reaction.message.channel
                if dsuggestions is None:
                    return
                dsuggestionschannel = client.get_channel(dsuggestions)
                msg = await channel.fetch_message(messageid)
                suggestioncheck = await client.get_channel(dsuggestions).history(limit=20).flatten()
                for sc in suggestioncheck:
                    if f'https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}' in sc.content:
                        return
                try:
                    finalcount = int(reaction.count - 1)
                    embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {reaction.message.channel.mention}")
                    embed1 = addEmbed(None,"dark_teal",embedDescription)
                    embed2 = msg.embeds[0]
                    await sendwebhook(reaction.message, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                except AttributeError as e:
                    print(f"{reaction.message.guild.name} doesn't have a demanded suggestions channel set.")
                return
        elif reaction.emoji == "❌":
            if reaction.count == rcount:
                rsuggestions = selectquery(sql, 'guilds', 'rejectedsuggestions', f'guild_id = {reaction.message.guild.id}')
                channel = reaction.message.channel
                if rsuggestions is None:
                    return
                rsuggestionschannel = client.get_channel(rsuggestions)
                msg = await channel.fetch_message(messageid)
                try:
                    suggestioncheck = await client.get_channel(rsuggestions).history(limit=20).flatten()
                    for sc in suggestioncheck:
                        if f'https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}' in sc.content:
                            return
                except AttributeError as e:
                    print(f"{rsuggestions} channel has no suggestion history.")
                try:
                    finalcount = int(reaction.count - 1)
                    embedDescription  = (f"**{finalcount} Downvotes:** [Go To Suggestion]({msg.jump_url}) - {reaction.message.channel.mention}")
                    embed1 = addEmbed(None,"dark_teal",embedDescription)
                    embed2 = msg.embeds[0]
                    await sendwebhook(reaction.message, "Rejected Suggestions", rsuggestionschannel, None, [embed1, embed2])
                except AttributeError as e:
                    print(f"{reaction.message.guild.name} doesn't have a rejected suggestions channel set.")
                return

@client.event
async def on_message(ctx):
    if not ctx.guild:
        return
    try:
        if str(ctx.guild.id) in str(betaannouncementguilds):
            channelnames = ["announcements", "updates", "competitions", "events"]
            for channel in channelnames:
                if channel in ctx.channel.name:
                    if not ctx.author.bot:
                        if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                            await client.process_commands(ctx)
                            return
                        else:
                            if ctx.attachments:
                                for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                    if imageextensions in ctx.attachments[0].filename:
                                        await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️", 1)
                                        return
                                await attachmentAutoEmbed(ctx, 0, "announcement", "👍", "❤️", 1)
                                return
                            if not ctx.attachments:
                                await ctx.delete()
                                embedDescription  = (f"{ctx.content}")
                                embed = addEmbed2(ctx,None,embedDescription )
                                sent = False
                                sent = await sendwebhook(ctx, ctx.author.name, ctx.channel, None, [embed])
                                while sent == True:
                                    msg = await ctx.channel.history(limit=1).flatten()
                                    msg = msg[0]
                                    await msg.add_reaction("👍")
                                    await msg.add_reaction("❤️")
                                    sent = False
                                print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
                        return
        channelnames = ["announcements", "updates", "competitions", "events"]
        for channel in channelnames:
            if channel in ctx.channel.name:
                if not ctx.author.bot:
                    if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                        await client.process_commands(ctx)
                        return
                    else:
                        if ctx.attachments:
                                for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                    if imageextensions in ctx.attachments[0].filename:
                                        await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️")
                                        return
                                await attachmentAutoEmbed(ctx, 0, "announcement", "👍", "❤️")
                                return
                        if not ctx.attachments:
                            await ctx.delete()
                            embedDescription  = (f"{ctx.content}")
                            msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                            await msg.add_reaction("👍")
                            await msg.add_reaction("❤️")
                            print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
        if "suggestions" in ctx.channel.name:
            if not ctx.author.bot:
                if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                    await client.process_commands(ctx)
                    return
                else:
                    if ctx.attachments:
                        for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                            if imageextensions in ctx.attachments[0].filename:
                                await attachmentAutoEmbed(ctx, 1, "suggestion", "✅", "❌")
                                return
                        await attachmentAutoEmbed(ctx, 0, "suggestion", "✅", "❌")
                        return
                    if not ctx.attachments:
                        await ctx.delete()
                        embedDescription  = (f"{ctx.content}")
                        msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❌")
                        print(f"A suggestion was made in #{ctx.channel.name} by {ctx.author}.")
        if "polls" in ctx.channel.name or "poll" in ctx.channel.name:
            if not ctx.author.bot:
                if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                    await client.process_commands(ctx)
                    return
                if ctx.webhook_id:
                    return
                else:
                    if ctx.attachments:
                        await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
                        file = discord.File(ctx.attachments[0].filename)
                        sent = True
                        await ctx.delete()
                        components1 = []
                        reactionstotal = {}
                        reactedusers = []
                        content = e.demojize(ctx.content)
                        messageemojis = re.findall(r'(:[^:]*:)', content)
                        if messageemojis is not None:
                            for emoji in messageemojis:
                                try:
                                    emoji1 = e.emojize(emoji)
                                    components1.append(Button(emoji=emoji1, id=emoji1))
                                    reactionstotal.update({emoji1: 0})
                                except: 
                                    pass
                            reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                        embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                        try:
                            msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription, f"attachment://{ctx.attachments[0].filename}"), components=[components1], file=file)
                        except HTTPException:
                            await ctx.channel.send("Please enter a message with emojis as options.", delete_after=3)
                        print(f"An image inclusive poll was made in #{ctx.channel.name} by {ctx.author}.")
                        while sent == True:
                            try:
                                res = await client.wait_for(event="button_click",check=lambda res: res.channel == ctx.channel, timeout=43200)
                                if res.user.id in reactedusers:
                                    await res.respond(
                                        type=InteractionType.ChannelMessageWithSource,
                                        content=f'You have already voted for this poll.'
                                    )
                                else:
                                    getdata = reactionstotal[res.component.id]
                                    reactionstotal.update({res.component.id: getdata + 1})
                                    reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                                    embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```"
                                    await msg.edit(embed=addEmbed(ctx,None,embedDescription1, f"attachment://{ctx.attachments[0].filename}"),
                                        components=[components1])
                                    await res.respond(
                                        type=InteractionType.ChannelMessageWithSource,
                                        content=f'Successfully voted for {res.component.id}.'
                                    )
                                    reactedusers.append(res.user.id)
                            except:
                                embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```\n\n **This poll has ended.**"
                                await msg.edit(embed=addEmbed(ctx,None,embedDescription1, f"attachment://{ctx.attachments[0].filename}"),
                                        components=[])
                                sent = False
                        os.remove(f"./{ctx.attachments[0].filename}")
                    if not ctx.attachments:
                        sent = True
                        await ctx.delete()
                        components1 = []
                        reactionstotal = {}
                        reactedusers = []
                        content = e.demojize(ctx.content)
                        messageemojis = re.findall(r'(:[^:]*:)', content)
                        if messageemojis is not None:
                            for emoji in messageemojis:
                                try:
                                    emoji1 = e.emojize(emoji)
                                    components1.append(Button(emoji=emoji1, id=emoji1))
                                    reactionstotal.update({emoji1: 0})
                                except: 
                                    pass
                            reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                            embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                            try:
                                msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ), components=[components1])
                            except HTTPException:
                                await ctx.channel.send("Please enter a message with emojis as options.", delete_after=3)
                        else:
                            embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                            msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ), components=[])
                        print(f"A poll was made in #{ctx.channel.name} by {ctx.author}.")
                        while sent == True:
                            try:
                                res = await client.wait_for(event="button_click",check=lambda res: res.channel == ctx.channel, timeout=43200)
                                if res.user.id in reactedusers:
                                    await res.respond(
                                        type=InteractionType.ChannelMessageWithSource,
                                        content=f'You have already voted for this poll.'
                                    )
                                else:
                                    getdata = reactionstotal[res.component.id]
                                    reactionstotal.update({res.component.id: getdata + 1})
                                    reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                                    embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```"
                                    await msg.edit(embed=addEmbed(ctx,None,embedDescription1 ),
                                        components=[components1])
                                    await res.respond(
                                        type=InteractionType.ChannelMessageWithSource,
                                        content=f'Successfully voted for {res.component.id}.'
                                    )
                                    reactedusers.append(res.user.id)
                            except:
                                embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```\n\n **This poll has ended.**"
                                try:
                                    await msg.edit(embed=addEmbed(ctx,None,embedDescription1 ),
                                            components=[])
                                except:
                                    pass
                                sent = False

        if "console-" in ctx.channel.name:
            messagestrip = await stripmessage(ctx.content, 'a server operator')
            if messagestrip:
                print(messagestrip)
                alertschannelcheck = selectquery(sql, 'guilds', 'alertschannel', f'guild_id = {ctx.guild.id}')
                generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
                if alertschannelcheck != 0:
                    alertschannel = client.get_channel(alertschannelcheck)
                    msg = await alertschannel.send(content=f'```{messagestrip}``` It originated from {ctx.channel.mention}!',
                    components=[Button(style=ButtonStyle.red, label="Verify", id=messagestrip)])
                    if generalchannelcheck != 0:
                        generalchannel = client.get_channel(generalchannelcheck)
                        await generalchannel.send(content=f'**WARNING!** `/op` or `/deop` was used. Check {alertschannel.mention} for more info.', delete_after=600)
                    verified = False
                    while verified == False:
                        res = await client.wait_for("button_click")
                        if res.component.id == messagestrip:
                            await msg.edit(content=f'```{messagestrip}``` It originated from {ctx.channel.mention}!',
                            components=[Button(style=ButtonStyle.green, disabled=True ,label=f"OP Verified By {res.user}")])
                            await res.respond(
                                type=InteractionType.ChannelMessageWithSource,
                                content=f'Op successfully verified.'
                            )
                            verified = True
            messagestrip = await stripmessage(ctx.content, 'Main thread terminated by WatchDog due to hard crash')
            if messagestrip:
                print(messagestrip)
                crashalertschannelcheck = selectquery(sql, 'guilds', 'crashalertschannel', f'guild_id = {ctx.guild.id}')
                generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
                if crashalertschannelcheck != 0:
                    crashalertschannel = client.get_channel(crashalertschannelcheck)
                    await crashalertschannel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
                    if generalchannelcheck != 0:
                        generalchannel = client.get_channel(generalchannelcheck)
                        await generalchannel.send(f'**WARNING!** {ctx.channel.mention} has just **hard crashed!** Check {crashalertschannel.mention} for more info.')
        if "console-" in ctx.channel.name:
            lptriggers = ["now inherits permissions from", "no longer inherits permissions from",
            "[LP] Set group.", "[LP] Web editor data was applied to user", "[LP] Web editor data was applied to group"]
            for trigger in lptriggers:
                messagestrip = await stripmessage(ctx.content, trigger)
                if messagestrip:
                    print(messagestrip)
                    lpalertschannelcheck = selectquery(sql, 'guilds', 'lpalertschannel', f'guild_id = {ctx.guild.id}')
                    if lpalertschannelcheck != 0:
                        lpalertschannel = client.get_channel(lpalertschannelcheck)
                        try:
                            await lpalertschannel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
                        except:
                            pass
        if ctx.guild.id in ham_guilds:
            if "console-" in ctx.channel.name:
                lptriggers = ["issued server command: /sudo", "issued server command: /attachcommand",
                "issued server command: /cmi attachcommand", "issued server command: /cmi sudo", 
                "issued server command: /npc command add", "issued server command: /ic", "issued server command: /cmi ic"]
                for trigger in lptriggers:
                    messagestrip = await stripmessage(ctx.content, trigger)
                    if messagestrip and "/icanhasbukkit" not in messagestrip:
                        print(messagestrip)
                        guildchannels = ctx.guild.channels
                        for channel in guildchannels:
                            if "command-alerts" in channel.name:
                                await channel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
        if ctx.guild.id in ham_guilds:
            if "console-survival" in ctx.channel.name:
                messagestrip = await stripmessage(ctx.content, '[HamAlerts] Thank you')
                if messagestrip:
                    print(messagestrip)
                    guildchannels = ctx.guild.channels
                    for channel in guildchannels:
                        if "receipts" in channel.name:
                            await channel.send(f'```{messagestrip}```')
    except Exception as e:
        print(e)

    await client.process_commands(ctx)

    return

client.run(TOKEN)  # Bot Run