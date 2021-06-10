import os
from discord.errors import HTTPException
import discord
from discord.ext import commands 
from discord_components import Button, ButtonStyle, InteractionType
import asyncio
import emoji as e
import re
from cogs.functions import *
from cogs.functions import *

class OnMessage(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if not ctx.guild:
            return
        try:
            if str(ctx.guild.id) in str(betaannouncementguilds):
                channelnames = ["announcements", "updates", "competitions", "events"]
                for channel in channelnames:
                    if channel in ctx.channel.name:
                        if not ctx.author.bot:
                            if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                                await client.process_commands(ctx)
                                return
                            else:
                                if ctx.attachments:
                                    for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                        if imageextensions in ctx.attachments[0].filename:
                                            await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️", 1)
                                            return
                                    await attachmentAutoEmbed(ctx, 0, "announcement", "👍", "❤️", 1)
                                    return
                                if not ctx.attachments:
                                    await ctx.delete()
                                    embedDescription  = (f"{ctx.content}")
                                    embed = addEmbed2(ctx,None,embedDescription )
                                    sent = False
                                    sent = await sendwebhook(ctx, ctx.author.name, ctx.channel, None, [embed])
                                    while sent == True:
                                        msg = await ctx.channel.history(limit=1).flatten()
                                        msg = msg[0]
                                        await msg.add_reaction("👍")
                                        await msg.add_reaction("❤️")
                                        sent = False
                                    print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
                            return
            channelnames = ["announcements", "updates", "competitions", "events"]
            for channel in channelnames:
                if channel in ctx.channel.name:
                    if not ctx.author.bot:
                        if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                            await client.process_commands(ctx)
                            return
                        else:
                            if ctx.attachments:
                                    for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                        if imageextensions in ctx.attachments[0].filename:
                                            await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️")
                                            return
                                    await attachmentAutoEmbed(ctx, 0, "announcement", "👍", "❤️")
                                    return
                            if not ctx.attachments:
                                await ctx.delete()
                                embedDescription  = (f"{ctx.content}")
                                msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                                await msg.add_reaction("👍")
                                await msg.add_reaction("❤️")
                                print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
            if "suggestions" in ctx.channel.name:
                if not ctx.author.bot:
                    if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                        await client.process_commands(ctx)
                        return
                    else:
                        if ctx.attachments:
                            for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                if imageextensions in ctx.attachments[0].filename:
                                    await attachmentAutoEmbed(ctx, 1, "suggestion", "✅", "❌")
                                    return
                            await attachmentAutoEmbed(ctx, 0, "suggestion", "✅", "❌")
                            return
                        if not ctx.attachments:
                            await ctx.delete()
                            embedDescription  = (f"{ctx.content}")
                            msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                            await msg.add_reaction("✅")
                            await msg.add_reaction("❌")
                            print(f"A suggestion was made in #{ctx.channel.name} by {ctx.author}.")
            if "polls" in ctx.channel.name or "poll" in ctx.channel.name:
                if not ctx.author.bot:
                    if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                        await client.process_commands(ctx)
                        return
                    if ctx.webhook_id:
                        return
                    else:
                        if ctx.attachments:
                            await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
                            file = discord.File(ctx.attachments[0].filename)
                            sent = True
                            await ctx.delete()
                            components1 = []
                            reactionstotal = {}
                            reactedusers = {}
                            content = e.demojize(ctx.content)
                            messageemojis = re.findall(r'(:[^:]*:)', content)
                            if messageemojis is not None:
                                for emoji in messageemojis:
                                    try:
                                        emoji1 = e.emojize(emoji)
                                        components1.append(Button(emoji=emoji1, id=emoji1))
                                        reactionstotal.update({emoji1: 0})
                                    except: 
                                        pass
                                reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                            embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                            try:
                                msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription, f"attachment://{ctx.attachments[0].filename}"), components=[components1], file=file)
                                reactedusers.update({msg.id: []})
                            except HTTPException:
                                await ctx.channel.send("Please enter a message with emojis as options.", delete_after=3)
                            print(f"An image inclusive poll was made in #{ctx.channel.name} by {ctx.author}.")
                            while sent == True:
                                try:
                                    res = await client.wait_for(event="button_click",check=lambda res: res.channel == ctx.channel, timeout=43200)
                                    if res.user.id in reactedusers:
                                        await res.respond(
                                            type=InteractionType.ChannelMessageWithSource,
                                            content=f'You have already voted for this poll.'
                                        )
                                    elif res.message.id != msg.id:
                                        pass
                                    else:
                                        getdata = reactionstotal[res.component.id]
                                        reactionstotal.update({res.component.id: getdata + 1})
                                        reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                                        embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```"
                                        await msg.edit(embed=addEmbed(ctx,None,embedDescription1, f"attachment://{ctx.attachments[0].filename}"),
                                            components=[components1])
                                        await res.respond(
                                            type=InteractionType.ChannelMessageWithSource,
                                            content=f'Successfully voted for {res.component.id}.'
                                        )
                                        reactedusers[msg.id].append(res.user.id)
                                except asyncio.TimeoutError:
                                    embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```\n\n **This poll has ended.**"
                                    await msg.edit(embed=addEmbed(ctx,None,embedDescription1, f"attachment://{ctx.attachments[0].filename}"),
                                            components=[])
                                    sent = False
                            os.remove(f"./{ctx.attachments[0].filename}")
                        if not ctx.attachments:
                            sent = True
                            await ctx.delete()
                            components1 = []
                            reactionstotal = {}
                            reactedusers = {}
                            content = e.demojize(ctx.content)
                            messageemojis = re.findall(r'(:[^:]*:)', content)
                            if messageemojis is not None:
                                for emoji in messageemojis:
                                    try:
                                        emoji1 = e.emojize(emoji)
                                        components1.append(Button(emoji=emoji1, id=emoji1))
                                        reactionstotal.update({emoji1: 0})
                                    except: 
                                        pass
                                reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                                embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                                try:
                                    msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ), components=[components1])
                                    reactedusers.update({msg.id: []})
                                except HTTPException:
                                    await ctx.channel.send("Please enter a message with emojis as options.", delete_after=3)
                            else:
                                embedDescription  = (f"{ctx.content}\n\n```{reactionstotal1}\n```")
                                msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ), components=[])
                            print(f"A poll was made in #{ctx.channel.name} by {ctx.author}.")
                            while sent == True:
                                try:
                                    res = await client.wait_for(event="button_click",check=lambda res: res.channel == ctx.channel, timeout=43200)
                                    if res.user.id in reactedusers[msg.id]:
                                        await res.respond(
                                            type=InteractionType.ChannelMessageWithSource,
                                            content=f'You have already voted for this poll.'
                                        )
                                    elif res.message.id != msg.id:
                                        pass
                                    else:
                                        getdata = reactionstotal[res.component.id]
                                        reactionstotal.update({res.component.id: getdata + 1})
                                        reactionstotal1 = str(reactionstotal).replace("{", " ").replace("}", "").replace(",", f"\n").replace(":", "").replace("'", "")
                                        embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```"
                                        await msg.edit(embed=addEmbed(ctx,None,embedDescription1 ),
                                            components=[components1])
                                        await res.respond(
                                            type=InteractionType.ChannelMessageWithSource,
                                            content=f'Successfully voted for {res.component.id}.'
                                        )
                                        reactedusers[msg.id].append(res.user.id)
                                except asyncio.TimeoutError:
                                    embedDescription1 = f"{ctx.content}\n\n```{reactionstotal1}\n```\n\n **This poll has ended.**"
                                    try:
                                        await msg.edit(embed=addEmbed(ctx,None,embedDescription1 ),
                                                components=[])
                                    except:
                                        pass
                                    sent = False

            if "console-" in ctx.channel.name:
                messagestrip = await stripmessage(ctx.content, 'a server operator')
                if messagestrip:
                    print(messagestrip)
                    alertschannelcheck = selectquery(sql, 'guilds', 'alertschannel', f'guild_id = {ctx.guild.id}')
                    generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
                    if alertschannelcheck != 0:
                        alertschannel = client.get_channel(alertschannelcheck)
                        msg = await alertschannel.send(content=f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!',
                        components=[Button(style=ButtonStyle.red, label="Verify", id=messagestrip)])
                        if generalchannelcheck != 0:
                            generalchannel = client.get_channel(generalchannelcheck)
                            await generalchannel.send(content=f'**WARNING!** `/op` or `/deop` was used. Check {alertschannel.mention} for more info.', delete_after=600)
                        verified = False
                        while verified == False:
                            res = await client.wait_for("button_click")
                            if res.component.id == messagestrip:
                                await msg.edit(content=f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!',
                                components=[Button(style=ButtonStyle.green, disabled=True ,label=f"OP Verified By {res.user}")])
                                await res.respond(
                                    type=InteractionType.ChannelMessageWithSource,
                                    content=f'Op successfully verified.'
                                )
                                verified = True
                messagestrip = await stripmessage(ctx.content, 'Main thread terminated by WatchDog due to hard crash')
                if messagestrip:
                    print(messagestrip)
                    crashalertschannelcheck = selectquery(sql, 'guilds', 'crashalertschannel', f'guild_id = {ctx.guild.id}')
                    generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
                    if crashalertschannelcheck != 0:
                        crashalertschannel = client.get_channel(crashalertschannelcheck)
                        await crashalertschannel.send(f'```{messagestrip}``` It originated from {ctx.channel.mention}!')
                        if generalchannelcheck != 0:
                            generalchannel = client.get_channel(generalchannelcheck)
                            await generalchannel.send(f'**WARNING!** {ctx.channel.mention} has just **hard crashed!** Check {crashalertschannel.mention} for more info.')
            if "console-" in ctx.channel.name:
                lptriggers = ["now inherits permissions from", "no longer inherits permissions from",
                "[LP] Set group.", "[LP] Web editor data was applied to user", "[LP] Web editor data was applied to group"]
                for trigger in lptriggers:
                    messagestrip = await stripmessage(ctx.content, trigger)
                    if messagestrip:
                        print(messagestrip)
                        lpalertschannelcheck = selectquery(sql, 'guilds', 'lpalertschannel', f'guild_id = {ctx.guild.id}')
                        if lpalertschannelcheck != 0:
                            lpalertschannel = client.get_channel(lpalertschannelcheck)
                            try:
                                await lpalertschannel.send(f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!')
                            except:
                                pass
            if ctx.guild.id in ham_guilds:
                if "console-" in ctx.channel.name:
                    lptriggers = ["issued server command: /sudo", "issued server command: /attachcommand",
                    "issued server command: /cmi attachcommand", "issued server command: /cmi sudo", 
                    "issued server command: /npc command add", "issued server command: /ic", "issued server command: /cmi ic"]
                    for trigger in lptriggers:
                        messagestrip = await stripmessage(ctx.content, trigger)
                        if messagestrip and "/icanhasbukkit" not in messagestrip:
                            print(messagestrip)
                            guildchannels = ctx.guild.channels
                            for channel in guildchannels:
                                if "command-alerts" in channel.name:
                                    await channel.send(f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!')
            if ctx.guild.id in ham_guilds:
                if "console-survival" in ctx.channel.name:
                    messagestrip = await stripmessage(ctx.content, '[HamAlerts] Thank you')
                    if messagestrip:
                        print(messagestrip)
                        guildchannels = ctx.guild.channels
                        for channel in guildchannels:
                            if "receipts" in channel.name:
                                await channel.send(f'```\n{messagestrip}\n```')
        except Exception as e1:
            return

def setup(client):
    client.add_cog(OnMessage(client))