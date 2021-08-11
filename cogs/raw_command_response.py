from multiprocessing.connection import Client
import discord
from discord.ext import commands 
from discord_components import Button, ButtonStyle, InteractionType, SelectOption, Select
from discord.ext import commands 
from utils.functions import *
from discord.http import Route
from munch import DefaultMunch
from discord.utils import get
import aiohttp

class raw_command_response(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_socket_response(self, res):
        inte = res
        undefined = object()
        res = DefaultMunch.fromDict(res, undefined)
        try:
            if res.t != "INTERACTION_CREATE":
                return
            if res.d.type != 2:
                return
            res = res.d
            interaction_id = res.id
            interaction_token = res.token
        except:
            return
        if res.data.type == 3:
            for item in res.data.resolved.messages.keys():
                resmessage = res.data.resolved.messages[item]
            chan = client.get_channel(int(resmessage.channel_id))
            guild = get(client.guilds, id=int(res.guild_id))
            member = get(guild.members, id=int(res.member.user.id))
            color = get(chan.guild.members, name=res.member.user.username).color
            if res.data.name.lower() == ("embed"):
                embed = addEmbed(None, "invis", "Message successfully embeded!")
                data = {
                        "embeds": [embed.to_dict()],
                        "components": [],
                        "flags": 64
                    }
                try:
                    embed = addEmbed(None, "invis", resmessage.content)
                    try:
                        embed2 = addEmbed(None, color, f"{resmessage.content}\n\n{resmessage.embeds[0].description}")
                    except:
                        embed2 = addEmbed(None, color, resmessage.content)
                    embed2.set_author(name=resmessage.author.username, icon_url=f"https://cdn.discordapp.com/avatars/{resmessage.author.id}/{resmessage.author.avatar}.png?size=2048")
                    if not await moderatorcheck(guild, member):
                        embed = addEmbed(None, "red", "You don't have permission to do this!")
                        data = {
                        "embeds": [embed.to_dict()],
                        "components": [],
                        "flags": 64
                        }
                        await self.bot.http.request(
                        Route(
                            "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                        ),
                        json={"type": 4, "data": data},
                        )
                        return
                    await chan.send(embed=embed2)
                    await self.bot.http.request(
                        Route(
                            "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                        ),
                        json={"type": 4, "data": data},
                    )
                except Exception as e:
                    print(e)
            elif res.data.name.lower() == ("edit embed"):
                if resmessage.embeds[0] is not None:
                    embed = addEmbed(None, "invis", "Please send the new announcement.")
                    data = {
                    "embeds": [embed.to_dict()],
                    "components": [],
                    "flags": 64
                    }
                    await self.bot.http.request(
                        Route(
                            "POST", f"/interactions/{interaction_id}/{interaction_token}/callback"
                        ),
                        json={"type": 4, "data": data},
                    )
                    try:
                        fulres = await client.wait_for('message', timeout=900, check=lambda x: x.channel == chan)
                        fulres2 = await client.wait_for('message', timeout=885, check=lambda x: x.channel == chan)
                        await asyncio.sleep(0.5)
                        try:
                            if fulres.content == fulres2.embeds[0].description:
                                await fulres2.delete()
                        except:
                            try:
                                await fulres.delete()
                            except:
                                pass
                    except asyncio.TimeoutError:
                        embed = addEmbed(None, "invis", "Embed editing has timed out.")
                        await client.http.request(
                        Route(
                            "PATCH", f"/webhooks/{res.application_id}/{interaction_token}/messages/@original"
                        ),
                        json={"embeds": [embed.to_dict()]},
                        )
                        return
                    embedDescription = fulres.content
                    msg = await chan.fetch_message(resmessage.id)
                    if msg.author.id != client.user.id:
                        webhook1 = await getwebhook(resmessage, "Ham5teakBot3", chan)
                        async with aiohttp.ClientSession() as session:
                            webh = discord.Webhook.from_url(webhook1.url, adapter=discord.AsyncWebhookAdapter(session=session))
                            try:
                                imageurl = (resmessage.embeds[0].image.url).split("/")[6]
                                embed = addEmbed2(None, color, embedDescription, f"attachment://{imageurl}")
                            except:
                                embed = addEmbed2(None, color, embedDescription, None)
                            await webh.edit_message(resmessage.id, embeds=[embed])
                    elif msg.author.id == client.user.id:
                        try:
                            imageurl = (resmessage.embeds[0].image.url).split("/")[6]
                            embed1 = addEmbed(None, color, embedDescription, f"attachment://{imageurl}")
                        except:
                            embed1 = addEmbed(None, color, embedDescription, None)
                        try:
                            embed1.set_author(name=resmessage.embeds[0].author.name, icon_url=resmessage.embeds[0].author.icon_url)
                        except:
                            pass
                        msg = chan.get_partial_message(resmessage.id)
                        await msg.edit(embed=embed1)
                    embed = addEmbed(None, "invis", "Announcement has been edited!")
                    await client.http.request(
                    Route(
                        "PATCH", f"/webhooks/{res.application_id}/{interaction_token}/messages/@original"
                    ),
                    json={"embeds": [embed.to_dict()]},
                    )

          
def setup(client):
    client.add_cog(raw_command_response(client))