from multiprocessing.connection import Client
import discord
from discord.ext import commands 
from discord_components import Button, ButtonStyle, InteractionType, SelectOption, Select
from discord.ext import commands 
from utils.functions import *
from discord.http import Route
from munch import DefaultMunch
from discord.utils import get

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

class on_socket_response(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_socket_response(self, res):
        undefined = object()
        res = DefaultMunch.fromDict(res, undefined)
        try:
            if res.t != "INTERACTION_CREATE":
                return
            if res.d.type != 3:
                return
            res = res.d
            interaction_id = res.id
            interaction_token = res.token
        except:
            return
        try:
            buttonlabel = res.message.components[0].components[0].label
            channelid = int(res.message.channel_id)
        except:
            buttonlabel = None
            channelid = int(res.channel_id)
        channel = self.bot.get_channel(channelid)
        try:
            msg = await channel.fetch_message(res.message.id)
        except Exception as e:
            msg = None
        if buttonlabel == "Verify" and msg != None:
            if not "a server operator" in msg.content:
                return
            await msg.edit(components=[Button(style=ButtonStyle.green, disabled=True ,label=f"OP Verified By {res.member.user.username}#{res.member.user.discriminator}")])
            data = {
                "content": "Op successfully verified.",
                "flags": 64
            }

            try:
                await self.bot.http.request(
                    Route(
                        "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                    ),
                    json={"type": 4, "data": data},
                )
            except Exception as e:
                print(e)
        elif msg != None and buttonlabel != None:
            if not "Ham5teak Bot Ticket Assistant" in msg.embeds[0].author.name:
                return
            try:
                if res.data.custom_id == "Item Lost":
                    embedDescription1 = f"1. **Item Lost Due To Server Lag/Crash** \n\n\`\`\`\nIn-game Name:\nServer:\nItems you lost:  \n\`\`\`\n\nIf they are enchanted tools, please mention the enchantments if possible."
                elif res.data.custom_id == "Issue or Bug Report":
                    embedDescription1 = f"2. **Issue/Bug Report** \n\n\`\`\`\nIn-Game Name : \nServer: \nIssue/Bug :\n\`\`\`"
                elif res.data.custom_id == "Same IP Connection":
                    embedDescription1 = f"3. **Same IP Connection** \n\n\`\`\`\nIn-Game Name of Same IP Connection : \n- \n- \n\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
                elif res.data.custom_id == "Connection Problems":
                    embedDescription1 = f"4. **Connection Problems** \n\n\`\`\`\nIn-game Name:\nWhat connection problem are you facing? Please explain briefly:\n\`\`\`\n\n"
                elif res.data.custom_id == "Discord Issue":
                    embedDescription1 = f"5. **Discord Issue** \nPlease state your issue and wait patiently until our support team arrives."
                elif res.data.custom_id == "Forgot Password":
                    embedDescription1 = f"6. **Forgot Password** \n\n\`\`\`\nIn-game Name:\nIP Address : (Format should be xxx.xxx.xxx.xxx)\n\`\`\`"
                elif res.data.custom_id == "Ban or Mute Appeal":
                    embedDescription1 = f"""7. **Ban/Mute Appeal** \n\n\`\`\`\nWhy did you get banned/muted? \nWas it on discord or in-game?\n\`\`\` \nIf it was in-game, what is your in-game name and who banned/muted you? 
                \nAlso - please do a ban appeal/mute appeal next time using https://ham5teak.xyz/forums/ban-appeal.21/"""
                elif res.data.custom_id == "Queries":
                    embedDescription1 = f"""8. **Queries** \nPlease state your questions here and wait patiently for a staff to reply.\nIf you have to do something at the moment, please leave a note for Staff."""
                elif res.data.custom_id == "In-Game Rank Parity":
                    embedDescription1 = f"""9. **In-Game Rank Parity** \nPlease state your In-Game Name and rank you would like to be paired.\nIf you have to do something at the moment, please leave a note for Staff.
                    \n\`\`\`\nIn-Game Name: \nRank: \n\`\`\`\n"""
                elif res.data.custom_id == "Role Application":
                    embedDescription1 = f"""10. **Role Application** \nPlease state the role you want to apply for `Youtuber/DJ/Dev-Chat`.
                    \nIf you're applying for youtuber please send a video you've recorded in Ham5teak if not please wait until our support team arrives."""
                if embedDescription1 is not None:
                    await msg.edit(embed=await embed1(embedDescription1),components=[
                    Button(style=ButtonStyle.green, label=f"{res.member.user.username}#{res.member.user.discriminator} chose {res.data.custom_id}", disabled=True)
                    ])
                options1 = []
                embed2 = await embed1(f"""{res.data.custom_id} chosen.""")
                for server in serversandcats.keys():
                    options1.append({"label": server, "value": serversandcats[server]})
                try:
                    data = {
                        "embeds": [embed2.to_dict()],
                        "components": [{
                        "type": 1,
                        "components": [{
                                "type": 3,
                                "custom_id": channel.name,
                                "options": options1,
                                "placeholder": "Choose a server",
                                "min_values": 1,
                                "max_values": 1
                            }]}],
                        "flags": 64
                    }
                    await self.bot.http.request(
                    Route(
                        "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                    ),
                    json={"type": 4, "data": data},
                    )
                except:
                    pass
                if "ticket-" in channel.name:
                    await channel.edit(name=f"{res.data.custom_id}-{res.member.user.username}")
                if channel.guild.id not in ham_guilds:
                    return
            except:
                pass
        elif res.data.component_type == 3 and int(res.application_id) == self.bot.user.id:
            chanid = int(res.data.__dict__["values"][0])
            cat = client.get_channel(chanid)
            try:
                await channel.edit(category=cat)
            except:
                pass
            for key, value in serversandcats.items():
                if value == chanid:
                    channame = key
                    embedDescription2 = f'{channame} selected as ticket category.'
                    embed2 = await embed1(embedDescription2)
                    data = {
                        "embeds": [embed2.to_dict()],
                        "flags": 64,
                        "components": []
                    }
                    try:
                        await self.bot.http.request(
                            Route(
                                "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                            ),
                            json={"type": 7, "data": data},
                        )
                    except Exception as e:
                        print(e)
                    return

def setup(client):
    client.add_cog(on_socket_response(client))