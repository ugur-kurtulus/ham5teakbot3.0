import discord
from discord.ext import commands 
from discord_components import Button, ButtonStyle, InteractionType, SelectOption, Select
from discord.ext import commands 
from utils.functions import *

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
            embed1.set_footer(text="Ham5teak Bot 3.0 | Made by Beastman#1937, SottaByte#1543 and Jaymz#7815")
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

def setup(client):
    client.add_cog(on_guild_channel_create(client))