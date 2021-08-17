import discord
from utils.functions import *
import discordpylogger

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
    guilds = []
    embeds = []
    for guild in client.guilds:
        result1 = selectqueryall(sql, 'announcements', 'channel_id', f'channel_type = "announcement" AND guild_id = {guild.id}')
        announcementschannels[guild.id] = []
        for type in result1:
            type1 = type[0]
            announcementschannels[guild.id].append(type1)
        result2 = selectqueryall(sql, 'announcements', 'channel_id', f'channel_type = "suggestion" AND guild_id = {guild.id}')
        suggestionchannels[guild.id] = []
        for type in result2:
            type1 = type[0]
            suggestionchannels[guild.id].append(type1)
        result3 = selectqueryall(sql, 'announcements', 'channel_id', f'channel_type = "poll" AND guild_id = {guild.id}')
        pollchannels[guild.id] = []
        for typepoll in result3:
            typepoll1 = typepoll[0]
            pollchannels[guild.id].append(typepoll1)
        guilds.append(guild)
    for i in range(len(guilds)):
        if i == 0:
            embed1 = addEmbed(None, "teal", "**__Guilds:__**")
            embeds.append(embed1)
        if guilds[i] in guilds[::25] and i != 0:
            newembed = addEmbed(None, "teal", "")
            embeds.append(newembed)
        embeds[-1].add_field(name=guilds[i].name, value=f"ID: `{guilds[i].id}`, Shard: `{calcshard(guilds[i].id)}`", inline=False)
    channel = client.get_channel(841245744421273620)
    for embed in embeds:
        await channel.send(embed=embed)
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'cogs.{filename[:-3]}')
                print(f"{filename[:-3]} has successfully been loaded!")
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                print(f"{filename[:-3]} is already loaded.")
    for filename in os.listdir('./cogs/games'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'cogs.games.{filename[:-3]}')
                print(f"{filename[:-3]} has successfully been loaded!")
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                print(f"{filename[:-3]} is already loaded.")
    client.remove_command('help')
    result = selectqueryall(sql, 'guilds', 'guild_id', 'betaannouncements = 1')
    for type in result:
        type1 = type[0]
        betaannouncementguilds.append(type1)
    while True:
        await statuscheck()

client.run(TOKEN)  # Bot Run