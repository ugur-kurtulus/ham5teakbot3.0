import discord
from discord.ext import commands 
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType
from discord_slash import cog_ext, SlashCommand
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select_option, create_select
from discord.ext import commands 
from discord_slash.model import ButtonStyle
from utils.functions import *
from discord.http import Route
from munch import DefaultMunch
from discord.utils import get
import emoji

async def embed1(embedDescription):
        embed1 = discord.Embed(description=f"{embedDescription}", color=discord.Color.dark_teal())
        embed1.set_author(name="Ham5teak Bot Ticket Assistant", icon_url="https://cdn.discordapp.com/icons/380308776114454528/a_be4514bb0a52a206d1bddbd5fbd2250f.png?size=4096")
        embed1.set_footer(text="Ham5teak Bot 3.0 | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
        return embed1

serversandcats = {
"Survival": 632946682207928321, "Skyblocks": 632946712805244948, "Semi-Vanilla": 667988805059346435, 
"Factions": 659020993553104896, "Prison": 632946839792123948, "Creative": 632946812092678154, 
"Caveblocks": 786399045081890858, "Minigames": 664805277991960586
}

class OnComponent(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_component(self, ctx):
        try:
            if ctx.component["label"] == "Verify" and ctx.component_type == 2:
                await ctx.origin_message.edit(components=[create_actionrow(create_button(style=ButtonStyle.green, label=f"OP Verified By {ctx.author.name}#{ctx.author.discriminator}", disabled=True))])
                await ctx.send("OP Successfully Verified", hidden=True)
                return
            if "Ham5teak Bot Ticket Assistant" in ctx.origin_message.embeds[0].author.name and ctx.component_type == 2:
                try:
                    datacustomid = ctx.data["custom_id"]
                    if ctx.data["custom_id"] == "Item Lost":
                        embedDescription1 = f"1. **Item Lost Due To Server Lag/Crash** \n\n\`\`\`\nIn-game Name:\nServer:\nItems you lost:  \n\`\`\`\n\nIf they are enchanted tools, please mention the enchantments if possible."
                    elif ctx.data["custom_id"] == "Issue or Bug Report":
                        embedDescription1 = f"2. **Issue/Bug Report** \n\n\`\`\`\nIn-Game Name : \nServer: \nIssue/Bug :\n\`\`\`"
                    elif ctx.data["custom_id"] == "Same IP Connection":
                        embedDescription1 = f"3. **Same IP Connection** \n\n\`\`\`\nIn-Game Name of Same IP Connection : \n- \n- \n\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
                    elif ctx.data["custom_id"] == "Connection Problems":
                        embedDescription1 = f"4. **Connection Problems** \n\n\`\`\`\nIn-game Name:\nWhat connection problem are you facing? Please explain briefly:\n\`\`\`\n\n"
                    elif ctx.data["custom_id"] == "Discord Issue":
                        embedDescription1 = f"5. **Discord Issue** \nPlease state your issue and wait patiently until our support team arrives."
                    elif ctx.data["custom_id"] == "Forgot Password":
                        embedDescription1 = f"6. **Forgot Password** \n\n\`\`\`\nIn-game Name:\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
                    elif ctx.data["custom_id"] == "Ban or Mute Appeal":
                        embedDescription1 = f"""7. **Ban/Mute Appeal** \n\n\`\`\`\nWhy did you get banned/muted? \nWas it on discord or in-game?\n\`\`\` \nIf it was in-game, what is your in-game name and who banned/muted you? 
                    \nAlso - please do a ban appeal/mute appeal next time using https://ham5teak.xyz/forums/ban-appeal.21/"""
                    elif ctx.data["custom_id"] == "Queries":
                        embedDescription1 = f"""8. **Queries** \nPlease state your questions here and wait patiently for a staff to reply.\nIf you have to do something at the moment, please leave a note for Staff."""
                    elif ctx.data["custom_id"] == "In-Game Rank Parity":
                        embedDescription1 = f"""9. **In-Game Rank Parity** \nPlease state your In-Game Name and rank you would like to be paired.\nIf you have to do something at the moment, please leave a note for Staff.
                        \n\`\`\`\nIn-Game Name: \nRank: \n\`\`\`\n"""
                    elif ctx.data["custom_id"] == "Role Application":
                        embedDescription1 = f"""10. **Role Application** \nPlease state the role you want to apply for `Youtuber/DJ/Dev-Chat`.
                        \nIf you're applying for youtuber please send a video you've recorded in Ham5teak if not please wait until our support team arrives."""
                    if embedDescription1 is not None:
                        await ctx.origin_message.edit(embed=await embed1(embedDescription1),components=[create_actionrow(create_button(style=ButtonStyle.green, label=f"{ctx.author.name}#{ctx.author.discriminator} chose {datacustomid}", disabled=True))])
                    options1 = []
                    embed2 = await embed1(f"{datacustomid} chosen.")
                    i = 1
                    numemoji = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 0: "0️⃣"}
                    for server in serversandcats.keys():
                        options1.append(create_select_option(label=server, value=str(serversandcats[server]), emoji=numemoji[i]))
                        i += 1
                    try:
                        await ctx.send(embed=embed2, components=[create_actionrow(create_select(options=options1, custom_id=f"{datacustomid}-{ctx.author.name}".lower(), placeholder="Choose a server", max_values=1, min_values=1))], hidden=True)
                    except:
                        pass
                    if "ticket-" in ctx.channel.name:
                        await ctx.channel.edit(name=f"{datacustomid}-{ctx.author.name}")
                    if ctx.channel.guild.id not in ham_guilds:
                        return
                except:
                    pass
        except TypeError:
            try:
                if ctx.component_id.replace(" ", "-") == ctx.channel.name:
                    cat = client.get_channel(int(ctx.data["values"][0]))
                    try:
                        await ctx.channel.edit(category=cat)
                    except:
                        pass
                    for key, value in serversandcats.items():
                        if value == int(ctx.data["values"][0]):
                            channame = key
                            embedDescription2 = f'{channame} selected as ticket category.'
                            embed2 = await embed1(embedDescription2)
                            data = {
                            "embeds": [embed2.to_dict()],
                            "flags": 64,
                            "components": []
                            }
                            await self.bot.http.request(
                                Route(
                                    "POST", f"/interactions/{ctx.interaction_id}/{ctx._token}/callback"
                                ),
                                json={"type": 7, "data": data},
                            )
                            return
            except Exception as e:
                print(e)
        except KeyError:
            pass
          
def setup(client):
    client.add_cog(OnComponent(client))