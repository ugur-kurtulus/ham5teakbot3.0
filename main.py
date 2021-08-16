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
    message = ""
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
        message += f"{guild.name}\n"
    embedDescription  = (f"**__Guilds:__ **\n{message}")
    channel = client.get_channel(841245744421273620)
    await channel.send(embed=addEmbed(None, "teal", embedDescription))
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f"{filename[:-3]} has successfully been loaded!")
    for filename in os.listdir('./cogs/games'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.games.{filename[:-3]}')
            print(f"{filename[:-3]} has successfully been loaded!")
    client.remove_command('help')
    result = selectqueryall(sql, 'guilds', 'guild_id', 'betaannouncements = 1')
    for type in result:
        type1 = type[0]
        betaannouncementguilds.append(type1)
    while True:
        await statuscheck()

client.run(TOKEN)  # Bot Run