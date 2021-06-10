from discord_components.select import Option
import discord
from discord.ext import commands 
from discord_components import Button, ButtonStyle, InteractionType, Select
from cogs.functions import *
from discord.ext import commands 
from cogs.functions import *

class on_guild_channel_create(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
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

def setup(client):
    client.add_cog(on_guild_channel_create(client))