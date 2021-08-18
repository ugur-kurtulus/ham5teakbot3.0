from multiprocessing.connection import Client
import discord
from discord.ext import commands 
from discord.ext import commands 
from utils.functions import *
from discord.http import Route
from munch import DefaultMunch
from discord.utils import get
from discord_slash import cog_ext
from discord_slash.context import ComponentContext, MenuContext
from discord_slash.model import ContextMenuType
import aiohttp
import aiofiles
import os
import datetime

class raw_command_response(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @cog_ext.cog_context_menu(name="User Info", target=ContextMenuType.USER)
    async def userinfo(self, ctx):
        guild = get(client.guilds, id=int(ctx.guild_id))
        resmember = ctx.target_author
        memberid = ctx.target_author.id
        chan = guild.get_channel(int(ctx.channel_id))
        resmemberobj = get(chan.guild.members, id=int(memberid))
        color = get(chan.guild.members, id=int(memberid)).color
        rolelist = []
        for role in resmember.roles:
            if role is not guild.default_role:
                rolelist.append(f"{role.mention}")
        if len(rolelist) > 47:
            displayedroles = f"{', '.join(rolelist[:42])} + {len(rolelist) - 42} more"
        else:
            displayedroles = ', '.join(rolelist)
        embed = addEmbed(ctx, color, "", None)
        embed.add_field(name="User Mention:", value=resmemberobj.mention, inline=True)
        embed.add_field(name="User Name:", value=f"{resmemberobj.name}#{resmemberobj.discriminator}")
        embed.add_field(name="Server Nickname:", value=resmember.nick)
        if resmemberobj.premium_since is not None:
            embed.add_field(name="Boosting Since:", value=str(resmemberobj.premium_since)[0:10], inline=True)
        else:
            embed.add_field(name="Server Boosts:", value="None", inline=True)
        embed.add_field(name="Server Join Date:", value=str(resmemberobj.joined_at)[0:10], inline=True)
        embed.add_field(name="Creation Date:", value=str(resmemberobj.created_at)[0:10], inline=True)
        embed.add_field(name="User Status:", value=f"`{resmemberobj.status}`".title(), inline=True)
        if resmemberobj.is_on_mobile() == False and str(resmemberobj.status) != "offline":
            embed.add_field(name="Device:", value=f"`Desktop`", inline=True)
        elif resmemberobj.is_on_mobile() == True and str(resmemberobj.status) != "offline":
            embed.add_field(name="Device:", value=f"`Mobile`", inline=True)
        else:
            embed.add_field(name="Device:", value=f"`Unknown`".title(), inline=True)
        try:
            if type(resmemberobj.activity) == discord.activity.CustomActivity and resmemberobj.activity.emoji:
                embed.add_field(name="Activity:", value=f"{resmemberobj.activity.emoji} `{resmemberobj.activity.name}`", inline=True)
            else:
                embed.add_field(name="Activity:", value=f"`{resmemberobj.activity.name}`", inline=True)
        except:
            embed.add_field(name="Activity:", value=f"`None`", inline=True)
        embed.add_field(name="User ID:", value=f"`{memberid}`", inline=False)
        embed.add_field(name="User Roles:", value=displayedroles, inline=False)
        embed.set_thumbnail(url=resmemberobj.avatar_url)
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_context_menu(name="Embed", target=ContextMenuType.MESSAGE)
    async def embed(self, ctx):
        guild = get(client.guilds, id=int(ctx.guild_id))
        chan = get(guild.channels, id=int(ctx.channel_id))
        if ctx.target_message.attachments != []:
            async with aiohttp.ClientSession() as session:
                url = ctx.target_message.attachments[0].url
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(ctx.target_message.attachments[0].filename, mode='wb')
                        await f.write(await resp.read())
                        await f.close()
            emimage = ctx.target_message.attachments[0].filename
            attach = f"attachment://{emimage}"
        elif ctx.target_message.attachments == []:
            emimage = None
            attach = None
        embed = addEmbed(None, "invis", "Message successfully embeded!")
        try:
            color = get(chan.guild.members, name=ctx.author.name).color
            try:
                embed2 = addEmbed(None, color, f"{ctx.target_message.content}\n\n{ctx.target_message.embeds[0].description}", attach)
            except:
                embed2 = addEmbed(None, color, ctx.target_message.content, attach)
            embed2.set_author(name=ctx.author.name, icon_url=f"https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png?size=2048")
            if not await moderatorcheck(guild, ctx.author):
                embed = addEmbed(None, "red", "You don't have permission to do this!")
                await ctx.send(embed=embed, hidden=True)
            if emimage is not None:
                await chan.send(embed=embed2, file=discord.File(emimage))
                os.remove(f"./{emimage}")
            else:
                await chan.send(embed=embed2)
            await ctx.send(embed=embed, hidden=True)
        except:
            pass

    @cog_ext.cog_context_menu(name="Edit Embed", target=ContextMenuType.MESSAGE)
    async def editembed(self, ctx):
        guild = get(client.guilds, id=int(ctx.guild_id))
        chan = get(guild.channels, id=int(ctx.channel_id))
        color = get(chan.guild.members, name=ctx.author.name).color
        try:
            if ctx.target_message.embeds[0] is not None:
                if not await moderatorcheck(guild, ctx.author):
                    embed = addEmbed(None, "red", "You don't have permission to do this!")
                    await ctx.send(embed=embed, hidden=True)
                    return
                embed = addEmbed(None, "invis", "Please send the new announcement.")
                await ctx.send(embed=embed, hidden=True)
                try:
                    fulres = await client.wait_for('message', timeout=900, check=lambda x: x.channel == chan)
                    if chan.id in announcementschannels[guild.id]:
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
                    else:
                        try:
                            await fulres.delete()
                        except:
                            pass
                except asyncio.TimeoutError:
                    embed = addEmbed(None, "invis", "Embed editing has timed out.")
                    await client.http.request(
                    Route(
                        "PATCH", f"/webhooks/{client.user.id}/{ctx._token}/messages/@original"
                    ),
                    json={"embeds": [embed.to_dict()]},
                    )
                    return
                embedDescription = fulres.content
                msg = await chan.fetch_message(ctx.target_message.id)
                if msg.author.id != client.user.id:
                    webhook1 = await getwebhook(ctx.target_message, "Ham5teakBot3", chan)
                    async with aiohttp.ClientSession() as session:
                        webh = discord.Webhook.from_url(webhook1.url, adapter=discord.AsyncWebhookAdapter(session=session))
                        try:
                            imageurl = (ctx.target_message.embeds[0].image.url).split("/")[6]
                            embed = addEmbed(None, color, embedDescription, f"attachment://{imageurl}")
                        except:
                            embed = addEmbed(None, color, embedDescription, None)
                        await webh.edit_message(ctx.target_message.id, embeds=[embed])
                elif msg.author.id == client.user.id:
                    try:
                        imageurl = (ctx.target_message.embeds[0].image.url).split("/")[6]
                        embed1 = addEmbed(None, color, embedDescription, f"attachment://{imageurl}")
                    except:
                        embed1 = addEmbed(None, color, embedDescription, None)
                    try:
                        embed1.set_author(name=ctx.target_message.embeds[0].author.name, icon_url=ctx.target_message.embeds[0].author.icon_url)
                    except:
                        pass
                    msg = chan.get_partial_message(ctx.target_message.id)
                    await msg.edit(embed=embed1)
                embed = addEmbed(None, "invis", "Announcement has been edited!")
                await client.http.request(
                Route(
                    "PATCH", f"/webhooks/{client.user.id}/{ctx._token}/messages/@original"
                ),
                json={"embeds": [embed.to_dict()]},
                )
        except:
            pass
          
def setup(client):
    client.add_cog(raw_command_response(client))