import discord
from utils.functions import *

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