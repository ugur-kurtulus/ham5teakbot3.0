import discord
from discord.ext import commands
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
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
3. **Player Report**
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
        
        msg = await channel.send(embed=await embed1(embedDescription),components=[
                    # Row 1
                    create_actionrow(create_button(style=ButtonStyle.green, label=f"1", custom_id="Item Lost"),
                    create_button(style=ButtonStyle.green, label=f"2", custom_id="Issue or Bug Report"),
                    create_button(style=ButtonStyle.green, label=f"3", custom_id="Player Report"),
                    create_button(style=ButtonStyle.green, label=f"4", custom_id="Connection Problems"),
                    create_button(style=ButtonStyle.green, label=f"5", custom_id="Discord Issue")),
                    # Row 2
                    create_actionrow(create_button(style=ButtonStyle.green, label=f"6", custom_id="Forgot Password"),
                    create_button(style=ButtonStyle.green, label=f"7", custom_id="Ban or Mute Appeal"),
                    create_button(style=ButtonStyle.green, label=f"8", custom_id="Queries"),
                    create_button(style=ButtonStyle.green, label=f"9", custom_id="In-Game Rank Parity"),
                    create_button(style=ButtonStyle.green, label=f"10", custom_id="Role Application"),),
                    # Row 3
                    create_actionrow(create_button(style=ButtonStyle.URL, label=f"Visit Store", url="http://shop.ham5teak.xyz/"),
                    create_button(style=ButtonStyle.URL, label=f"Visit Forums", url="https://ham5teak.xyz/")),
                    ])

def setup(client):
    client.add_cog(on_guild_channel_create(client))