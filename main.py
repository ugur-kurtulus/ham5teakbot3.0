import os
from discord import channel, voice_client
from discord.ext.commands.errors import UserNotFound
from dns.resolver import query
from dotenv import load_dotenv
from discord.utils import get  # New import
import discord
from discord.ext import commands  # New import
from discord_slash import SlashCommand, SlashContext
from mcstatus import MinecraftServer
import asyncio
import mysql.connector

client = commands.Bot(command_prefix='-')  # Defines prefix and bot
slash = SlashCommand(client, sync_commands=False)  # Defines slash commands

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
    query = (f'DELETE FROM {table} WHERE {where}')
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
    query = (f'SELECT {column} FROM {table} WHERE {wherenew}')
    try:
        with sql as sql:
            sql.connect()
            querycursor = sql.cursor()
            querycursor.execute(query)  
            result = querycursor.fetchone()[0]
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

def selectqueryall(sql, table , column, where):
    sql.connect()
    if where is not None:
        query = (f'SELECT {column} FROM {table} WHERE {where}')
    if where is None:
        query = (f'SELECT {column} FROM {table}')
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
        query = (f'INSERT INTO {table} {column} VALUES(%s'+(size-1)*(',%s')+')')
        print(query)
    else:
        query = (f'UPDATE {table} SET {column} = {values}' + f' WHERE {where}')
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

quilds_query = ('''
        CREATE TABLE guilds 
            (guild_id BIGINT NOT NULL PRIMARY KEY,
            guild_name VARCHAR(255) NOT NULL,
            premium BOOLEAN,
            administrator_id BIGINT,
            moderator_id BIGINT,
            generalchannel BIGINT,
            statuschannel BIGINT,
            alertschannel BIGINT,
            lpalertschannel BIGINT,
            crashalertschannel BIGINT,
            demandedsuggestions BIGINT,
            acceptedsuggestions BIGINT,
            rejectedsuggestions BIGINT)''')
categories_query = ('''
        CREATE TABLE categories 
            (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            FOREIGN KEY(guild_id) REFERENCES guilds(guild_id),
            category_id BIGINT,
            category_name VARCHAR(255),
            category_less VARCHAR(255)
            )''') 


sql = sqlconnect()      
createtable(sql,'guilds', quilds_query)
createtable(sql,'categories', categories_query)
premium_guilds = [selectqueryall(sql, 'guilds', 'guild_id', None)]
ham_guilds = [380308776114454528, 841225582967783445, 82038346120232967, 650658756803428381, 571626209868382236, 631067371661950977]

# ------- FUNCTIONS -------

async def stripmessage(string, targetstring):
    if targetstring in string:
            stringlist = string.split(f"\n")
            for stringa in stringlist:
                if targetstring in stringa:
                    return stringa

async def moderatorcheck(guild, member):
    if not guild:
        return 1
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
            if status.latency >= 1:
                ham5teak = "Online ✅"
            else:
                ham5teak = "Offline ❌"
            embed = discord.Embed(description=f"**Ham5teak Status:** {ham5teak} \n**Players:** {status.players.online}\n**IP:** play.ham5teak.xyz\n**Versions:** 1.13.x, 1.14.x, 1.15.x, 1.16.x", color=discord.Color.teal())
            embed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            embed.set_author(name="Ham5teak Network Status", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
            await channel.send(embed=embed)
            print(f"{guild.name} status successfully sent!")
        except:
            print(f"{guildname} doesn't have a status channel set.")
    await asyncio.sleep(600)

def addEmbed(ctx , color, new):
    if ctx != None:
        newEmbed = discord.Embed(description=f"{new}", color=ctx.author.color)
        newEmbed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
    else:
        newEmbed = discord.Embed(description=f"{new}", color=color)
        newEmbed.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
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
    embedDiscription  = (f"**__Guilds:__ **\n{message}")
    channel = client.get_channel(841245744421273620)
    await channel.send(embed=addEmbed(None,discord.Color.teal(), embedDiscription ))
    await statuscheck()

# ------- CLIENT COMMANDS -------

@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount:int):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)
    embedDiscription  = (f"{amount} messages were successfully deleted.")
    await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)

@client.command()
@discord.ext.commands.has_guild_permissions(manage_guild=True)
async def setup(ctx, password, admin_role_id:discord.Role,mod_role_id:discord.Role):
    await ctx.message.delete()
    guild_id = ctx.guild.id
    if guild_id in premium_guilds:
        embedDiscription  = (f"You are already Logged in as Premium")
        await ctx.send(embed=addEmbed(ctx,discord.Color.blue,embedDiscription ))
        return
    else:
        guild_name = ctx.guild.name
        column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
        values = (guild_id , guild_name , True , admin_role_id.id , mod_role_id.id)
        where = None
        result = (insertquery(sql, 'guilds' , column , values, where))
        query = 'SELECT guild_id FROM guilds NATURAL JOIN categories'
        sql.connect()
        querycursor = sql.cursor()
        querycursor.execute(query)  
        result = querycursor.fetchall()
        sql.commit()
        querycursor.close()        
        if (result == 0):
            embedDiscription  = (f"Registered successfully")
            await ctx.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ), delete_after=5)
        else:
            embedDiscription  = (f"Register Failed")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)

@client.command()
async def edit(ctx, id, *, embedDiscription):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    await ctx.channel.get_partial_message(id).edit(embed = addEmbed(ctx, id, embedDiscription ))

@client.command()
async def setchannel(ctx, command, channel: discord.TextChannel):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    guild_id = ctx.guild.id
    channelid = str(channel.id)
    commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
    , "rejectedsuggestions", "acceptedsuggestions", "demandedsuggestions"]
    for commanda in commandsloop:
        if commanda == command:
            print(f"{commanda} {channelid}")
            column = (command)
            values = (channelid)
            where = (f"guild_id = {guild_id}")
            result = (insertquery(sql, 'guilds', column , values, where))
            if (result == 0):
                embedDiscription  = (f"Successfully registered {command} as `{channel.id}`")
                await ctx.channel.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ), delete_after=5)
            else:
                embedDiscription  = (f"Couldn't register {command} as {channelid}")
                await ctx.channel.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)     

@client.command()
@commands.has_permissions(manage_messages=True)
async def move(ctx, alias):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    sql.connect()
    mycursor = sql.cursor()
    mycursor.execute(f"SELECT category_name FROM categories WHERE guild_id = {ctx.guild.id}")
    aliaslist = mycursor.fetchall()
    mycursor.close()
    for stralias in aliaslist:
        if alias == stralias[0]:
            ctxchannel = ctx.channel
            sql.connect()
            mycursor = sql.cursor()
            mycursor.execute(f"SELECT category_id FROM categories WHERE category_name = '{alias}' AND guild_id = {ctx.guild.id}")
            result = mycursor.fetchone()
            mycursor.close()
            cat = client.get_channel(result[0])
            await ctxchannel.edit(category=cat)
            embedDiscription  = (f"{ctxchannel.mention} has been moved to category {alias}")
            await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)

@client.command()
@commands.has_permissions(manage_guild=True)
async def setmove(ctx, categoryi: discord.CategoryChannel, alias):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    guild_id = ctx.guild.id
    categoryid = str(categoryi.id)
    categoryname = alias
    if guild_id not in premium_guilds:
        embedDiscription  = (f"You need premium to use this command.")
        await ctx.send(embed=addEmbed(ctx,discord.Color.blue,embedDiscription ))
        return
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            embedDiscription  =(f"Category `{categoryname}` already exists.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)
            return 1
    print(f"{categoryid} {categoryname}")
    column = '(guild_id, category_id)'
    values = (guild_id, categoryid)
    where = None
    result = (insertquery(sql, 'categories', column , values, where))
    column = ('category_name')
    values = (f"'{categoryname}'")
    where = (f"category_id = {categoryid}")
    result = (insertquery(sql, 'categories', column , values, where))
    if (result == 0):
        embedDiscription =(f"Successfully registered {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)    
    else:
        embedDiscription  =(f"Couldn't register {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)

@client.command()
@commands.has_permissions(manage_guild=True)
async def removemove(ctx, alias):
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    categoryname = alias
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            categoryn = deletequery(sql, 'categories', f"category_name = '{categoryname}'")
            embedDiscription  =(f"Category `{categoryname}` has been removed.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ), delete_after=5)
            return 1
    embedDiscription  =(f"Category `{categoryname}` couldn't be removed.")
    await ctx.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ), delete_after=5)
    return 1
    
@client.command(aliases=['ml'])
@commands.has_permissions(manage_guild=True)
async def movelist(ctx):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.message.delete()
    categories = [selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')]
    for category in categories:
        if categories == 0:
            embedDiscription  = ("You don't have any categories set")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=5)
            return
        newcat = str(category).replace('(', '').replace(')', '').replace('(', '').replace("'", '').replace("[", '').replace("]", '').replace(',', '').replace(' ', f'\n')
        embedDiscription  = (f"__**Categories you can move channels to:**__\n{newcat}")
        await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ), delete_after=10)        

# ------- ERROR HANDLERS -------

@move.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.delete()
        error = await ctx.send('Please enter the command correctly. `-move <category>`')
        await asyncio.sleep(5)
        await error.delete()

@setmove.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.ChannelNotFound):
        await ctx.message.delete()
        error = await ctx.send('Please enter a valid category id. `-setmove <categoryid> <alias>`')
        await asyncio.sleep(5)
        await error.delete()
        
@removemove.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.delete()
        error = await ctx.send('Please enter a valid category name. `-removemove <categoryname>`')
        await asyncio.sleep(5)
        await error.delete()


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

@purge.error
async def clear_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.message.delete()
        error = await ctx.send('Please make sure to enter a number. `-purge <amount>`')
        await asyncio.sleep(5)
        await error.delete()

# ------- SLASH COMMANDS -------
    
@slash.slash(name="accept")
async def accept(ctx, messageid):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    print(moderatorcheck1)
    if moderatorcheck1 == 0:
        await ctx.defer(hidden=True)
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    result = selectquery(sql, 'guilds', 'acceptedsuggestions', f'guild_id = {ctx.guild.id}')
    if result == 0:
        embedDiscription  = (f"This server doesn't have an accepted suggestions channel set.")
        await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDiscription ), hidden=True)
    else:
        msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
        for reaction in msg.reactions:
            if reaction.emoji != "✅":
                return 
            else:
                await ctx.defer(hidden=True)
                reactiona = reaction
                aschannel = client.get_channel(result)
                embedDiscription  = (f"**{reactiona.count} Upvotes:** [Go To Suggestion]({msg.jump_url}) - Suggestion was made in: {ctx.channel.mention}")
                await aschannel.send(embed=addEmbed(ctx,discord.Color.blue,embedDiscription ))
                await aschannel.send(embed=msg.embeds[0])
                embedDiscription  = (f"[Suggestion]({msg.jump_url}) successfully accepted!")
                await ctx.send(embed=addEmbed(ctx,discord.Color.blue,embedDiscription ))
                return

@slash.slash(name="ham5teak", description="View Ham5teak network status")
async def ham5teak(ctx):
    server = MinecraftServer.lookup("play.ham5teak.xyz:25565")
    status = server.status()
    if status.latency >= 1:
        ham5teak = "Online ✅"
    else:
        ham5teak = "Offline ❌"
    print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
    embedDiscription =(f"**Ham5teak Status:** {ham5teak} \n **Players:** {status.players.online}")
    await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))  

@slash.slash(name="help")
async def help(ctx):
    await ctx.defer(hidden=True)
    embedDiscription  = (f"Feature coming soon!")
    await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))

@slash.slash(name="move", description="Move a channel to specified category.", )
async def move(ctx, category):
    await ctx.defer(hidden=True)
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    if moderatorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
        return
    alias = category
    sql.connect()
    mycursor = sql.cursor()
    mycursor.execute(f"SELECT category_name FROM categories WHERE guild_id = {ctx.guild.id}")
    aliaslist = mycursor.fetchall()
    mycursor.close()
    for stralias in aliaslist:
        if alias == stralias[0]:
            ctxchannel = ctx.channel
            sql.connect()
            mycursor = sql.cursor()
            mycursor.execute(f"SELECT category_id FROM categories WHERE category_name = '{alias}' AND guild_id = {ctx.guild.id}")
            result = mycursor.fetchone()
            mycursor.close()
            cat = client.get_channel(result[0])
            await ctxchannel.edit(category=cat)
            embedDiscription  = (f"{ctxchannel.mention} has been moved to category {alias}")
            await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))

@slash.slash(name="tag", description="A command used to leave a note to a channel")
async def tag(ctx, note, user:discord.User = None, channel:discord.TextChannel = None, role:discord.Role = None):
    moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
    print(moderatorcheck1)
    if moderatorcheck1 == 0:
        await ctx.defer(hidden=True)
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), delete_after=5)
        return
    await ctx.defer(hidden=False)
    print(f"{note} {user} {channel} {role}")
    finalmentions = []
    mentions = [user, channel, role]
    for mention in mentions:
        if mention is not None:
            if finalmentions == 0:
                finalmentions.insert(mention.mention)
                print(', '.join(finalmentions))
            finalmentions.append(mention.mention)
            print(', '.join(finalmentions))
    for mention in mentions:
        if mention is not None:
            print(finalmentions)
            print("message has a mention")
            embedDiscription =(f"{ctx.author.mention} has tagged the channel as `{note.upper()}` \n\n**Mentions:** {', '.join(finalmentions)}")
            await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
            return
    print("message doesn't have mentions")
    embedDiscription  = (f"{ctx.author.mention} has tagged the channel as `{note.upper()}`")
    await ctx.send(embed=addEmbed(ctx,None,embedDiscription )) 

# ------- SETTING SLASH COMMANDS -------

@slash.slash(name="setchannel", description="Set channels for your server")
@commands.has_permissions(manage_guild=True)
async def setchannel(ctx, value: discord.TextChannel, channel):
    await ctx.defer(hidden=True)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
        return
    guild_id = ctx.guild.id
    channelid = str(value.id)
    commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
    , "acceptedsuggestions", "rejectedsuggestions", "demandedsuggestions"]
    for commanda in commandsloop:
        if commanda == channel:
            print(f"{commanda} {channelid}")
            column = (channel)
            values = (channelid)
            where = (f"guild_id = {guild_id}")
            result = (insertquery(sql, 'guilds', column , values, where))
            if result is not None:
                embedDiscription  = (f"{channel} successfully registered as <#{channelid}>")
                await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))
            else:
                embedDiscription  = (f"{channel} couldn't be registered as {channelid}")
                await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))  
        
@slash.slash(name="setmove")
@commands.has_permissions(manage_guild=True)
async def setmove(ctx, categoryi: discord.CategoryChannel, alias):
    await ctx.defer(hidden=True)
    await administratorcheck(ctx.guild, ctx.author)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
        return
    guild_id = ctx.guild.id
    categoryid = str(categoryi.id)
    categoryname = alias
    categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
    for stralias in categoryn:
        if categoryname == stralias[0]:
            embedDiscription  =(f"Category `{categoryname}` already exists.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))
            return 1
    print(f"{categoryid} {categoryname}")
    column = '(guild_id, category_id)'
    values = (guild_id, categoryid)
    where = None
    result = (insertquery(sql, 'categories', column , values, where))
    column = ('category_name')
    values = (f"'{categoryname}'")
    where = (f"category_id = {categoryid}")
    result = (insertquery(sql, 'categories', column , values, where))
    if (result == 0):
        embedDiscription =(f"Successfully registered {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))   
    else:
        embedDiscription  =(f"Couldn't register {categoryname} as `{categoryid}`")
        await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))

@slash.slash(name="setrole")
@commands.has_permissions(manage_guild=True)
async def setrole(ctx, administrator:discord.Role, moderator: discord.Role):
    await ctx.defer(hidden=True)
    administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
    if administratorcheck1 == 0:
        embedDiscription  = (f"You don't have permission to do this.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
        return
    print(f"{administrator.id} {moderator.id}")
    result = selectquery(sql, 'guilds', 'moderator_id', f'guild_id = {ctx.guild.id}')
    if result is None:
        embedDiscription  = (f"Server needs to be setup before executing this command.")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ))
    elif result is not None:
        a = insertquery(sql, "guilds", "moderator_id", f"{moderator.id}", f"guild_id = {ctx.guild.id}")
        b = insertquery(sql, "guilds", "administrator_id", f"{administrator.id}", f"guild_id = {ctx.guild.id}")
        if (a == 0) and (b == 0):
            embedDiscription  = (f"New administrator and moderator roles have successfully been set as {administrator.mention} {moderator.mention}")
            await ctx.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ))
        else:
            embedDiscription  = (f"Couldn't register {administrator.mention} {moderator.mention} as administrator and moderator.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))

@slash.slash(name="setup")
@commands.has_permissions(manage_guild=True)
async def setup(ctx, password, administrator:discord.Role, moderator:discord.Role):
    await ctx.defer(hidden=True)
    print(password)
    guild_id = ctx.guild.id
    if guild_id in premium_guilds:
        embedDiscription  = (f"You are already logged in as Premium")
        await ctx.send(embed=addEmbed(ctx,discord.Color.blue,embedDiscription ))
        return
    else:
        guild_name = ctx.guild.name
        column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
        values = (guild_id , guild_name , True , administrator.id , moderator.id)
        where = None
        await insertquery(sql, 'guilds' , column , values, where)
        insertcheck = selectquery(sql, 'guilds', 'premium', f'guild_id = {ctx.guild.id}')    
        if (insertcheck != 0):
            embedDiscription  = (f"Setup successfully completed!")
            await ctx.send(embed=addEmbed(ctx,discord.Color.green,embedDiscription ))
        else:
            embedDiscription  = (f"Setup failed!")
            await ctx.send(embed=addEmbed(ctx,discord.Color.red,embedDiscription ))

# ------- SLASH COMMAND ERROR HANDLERS -------

@client.event
async def on_slash_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingPermissions):
        await ctx.defer(hidden=True)
        embedDiscription  = (f"Please make sure you have entered all values correctly.\n {error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), hidden=True)
    if isinstance(error, commands.ChannelNotFound):
        await ctx.defer(hidden=True)
        embedDiscription  = (f"Please make sure you have entered all values correctly.\n {error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), hidden=True)
    if isinstance(error, commands.RoleNotFound):
        await ctx.defer(hidden=True)
        embedDiscription  = (f"Please make sure you have entered all values correctly.\n {error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), hidden=True)
    if isinstance(error, commands.MemberNotFound):
        await ctx.defer(hidden=True)
        embedDiscription  = (f"Please make sure you have entered all values correctly.\n {error}")
        await ctx.send(embed=addEmbed(ctx,None,embedDiscription ), hidden=True)

# ------- EVENT HANDLERS -------

@client.event
async def on_guild_channel_create(channel):
    if "ticket-" in channel.name:
        if channel.guild.id not in ham_guilds:
            return
        async def embed1(embedDescription1):
            embed1 = discord.Embed(description=embedDescription1, color=discord.Color.dark_teal())
            embed1.set_footer(text="Ham5teak Bot 3.0 | play.ham5teak.xyz | Made by Beastman#1937 and Jaymz#7815")
            embed1.set_author(name="Ham5teak Bot Ticket Assistant", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
            return embed1
        embedDescription = f"""Hello! The staff team will be assisting you shortly.
In order to make this process easier for us staff, please choose from
the following choices by replying with the respective options
(E.g : send a single number as a message) : 

**1**. **Item Lost** 
**2**. **Reporting an Issue/Bug** 
**3**. **Same IP Connection** 
**4**. **Connection Problems**
**5**. **Forgot Password**
**6**. **Ban/Mute Appeal**
**7**. **Queries**"""
        await channel.send(embed=await embed1(embedDescription))
        response = []
        def check1(m):
            options = ["1", "2", "3", "4", "5", "6", "7"]
            for option in options:
                if m.content == option:
                    response.append(int(option))
                    return m.content == option
        await client.wait_for("message", check=check1)
        await channel.purge(limit=1)
        if 1 in response:
            embedDescription1 = f"1. **Item Lost Due To Server Lag/Crash** \nIn-game Name:\nServer:\nItems you lost:  \n\nIf they are enchanted tools, please mention the enchantments if possible."
            await channel.send(embed=await embed1(embedDescription1))
        elif 2 in response:
            embedDescription1 = f"2. **Issue/Bug Report** \nIn-Game Name : \nServer: \nIssue/Bug :"
            await channel.send(embed=await embed1(embedDescription1))
        elif 3 in response:
            embedDescription1 = f"3. **Same IP Connection** \nIn-Game Name of Same IP Connection : \n- \n- \n\nIP Address : (Format should be xxx.xxx.xxx.xxx)"
            await channel.send(embed=await embed1(embedDescription1))
        elif 4 in response:
            embedDescription1 = f"4. **Connection Problems** \nIn-game Name:\n\nWhat connection problem are you facing? Please explain briefly."
            await channel.send(embed=await embed1(embedDescription1))
        elif 5 in response:
            embedDescription1 = f"5. **Forgot Password** \nIn-game Name:\nIP Address : (Format should be xxx.xxx.xxx.xxx)"
            await channel.send(embed=await embed1(embedDescription1))
        elif 6 in response:
            embedDescription1 = f"""6. **Ban/Mute Appeal** \nWhy did you get banned/muted? \nWas it on discord or in-game? 
            \n\nIf it was in-game, what is your in-game name and who banned/muted you? 
            \nAlso - please do a ban appeal/mute appeal next time using https://ham5teak.xyz/forums/ban-appeal.21/"""
            await channel.send(embed=await embed1(embedDescription1))
        elif 7 in response:
            embedDescription1 = f"""7. **Queries** \nPlease state your questions here and wait patiently for a staff to reply.
             If you have to do something at the moment, please leave a note for Staff."""
            await channel.send(embed=await embed1(embedDescription1))
        response.clear()

@client.event
async def on_reaction_add(reaction, user):
    messageid = reaction.message.id
    rcount = 2
    if "suggestions" not in reaction.message.channel.name:
        return
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
                await dsuggestionschannel.send(f'**{reaction.count} upvotes:** https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}',embed=msg.embeds[0])
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
                await rsuggestionschannel.send(f'**{reaction.count} downvotes:** https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}',embed=msg.embeds[0])
            except AttributeError as e:
                print(f"{reaction.message.guild.name} doesn't have a rejected suggestions channel set.")
            return

@client.event
async def on_message(ctx):
    if not ctx.guild:
        return
    channelnames = ["announcements", "updates", "competitions", "events"]
    for channel in channelnames:
        if channel in ctx.channel.name:
            if not ctx.author.bot:
                if ctx.content.startswith(client.command_prefix):
                    await client.process_commands(ctx)
                else:
                    if ctx.attachments:
                        await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
                        file = discord.File(ctx.attachments[0].filename)
                        embedDiscription  = (f"{ctx.content}")
                        embed = addEmbed(ctx,None,embedDiscription )
                        embed.set_image(url=f"attachment://{ctx.attachments[0].filename}")
                        msg = await ctx.channel.send(embed=embed, file=file)
                        await msg.add_reaction("👍")
                        await msg.add_reaction("❤️")
                        print(f"An image inclusive announcement was made in #{ctx.channel.name} by {ctx.author}.")
                        await ctx.delete()
                        os.remove(f"./{ctx.attachments[0].filename}")
                    if not ctx.attachments:
                        await ctx.delete()
                        embedDiscription  = (f"{ctx.content}")
                        msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDiscription ))
                        await msg.add_reaction("👍")
                        await msg.add_reaction("❤️")
                        print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
    channelnames = ["suggestions", "polls"]
    for channel in channelnames:
        if channel in ctx.channel.name:
            if not ctx.author.bot:
                if ctx.content.startswith(client.command_prefix):
                    await client.process_commands(ctx)
                else:
                    if ctx.attachments:
                        await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
                        file = discord.File(ctx.attachments[0].filename)
                        embedDiscription  = (f"{ctx.content}")
                        embed = addEmbed(ctx,None,embedDiscription )
                        embed.set_image(url=f"attachment://{ctx.attachments[0].filename}")
                        msg = await ctx.channel.send(embed=embed, file = file)
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❌")
                        print(f"An image inclusive suggestion was made in #{ctx.channel.name} by {ctx.author}.")
                        await ctx.delete()
                        os.remove(f"./{ctx.attachments[0].filename}")
                    if not ctx.attachments:
                        await ctx.delete()
                        embedDiscription  = (f"{ctx.content}")
                        msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDiscription ))
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❌")
                        print(f"A suggestion was made in #{ctx.channel.name} by {ctx.author}.")

    await client.process_commands(ctx)

    if "console-" in ctx.channel.name:
        messagestrip = await stripmessage(ctx.content, 'a server operator')
        if messagestrip:
            print(messagestrip)
            alertschannelcheck = selectquery(sql, 'guilds', 'alertschannel', f'guild_id = {ctx.guild.id}')
            generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
            if alertschannelcheck != 0:
                alertschannel = client.get_channel(alertschannelcheck)
                await alertschannel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
                if generalchannelcheck != 0:
                    generalchannel = client.get_channel(generalchannelcheck)
                    await generalchannel.send(f'**WARNING!** `/op` or `/deop` was used. Check {alertschannel.mention} for more info.')
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
    if "console-lobby" in ctx.channel.name:
        lptriggers = ["now inherits permissions from", "no longer inherits permissions from", "[LP] Demoting",
         "[LP] Promoting", "[LP] Web editor data was applied", "[LP] LOG > webeditor", "[LP] LOG > (Console@"
         , "[LP] Set"]
        for trigger in lptriggers:
            messagestrip = await stripmessage(ctx.content, trigger)
            if messagestrip:
                print(messagestrip)
                lpalertschannelcheck = selectquery(sql, 'guilds', 'lpalertschannel', f'guild_id = {ctx.guild.id}')
                if lpalertschannelcheck != 0:
                    lpalertschannel = client.get_channel(lpalertschannelcheck)
                    await lpalertschannel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
    return

client.run(TOKEN)  # Changes