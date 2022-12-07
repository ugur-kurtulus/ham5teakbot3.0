from logging import exception
import os
from discord.embeds import Embed
from discord.errors import HTTPException
import discord
from discord.ext import commands 
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
import asyncio
import emoji as e
import re
import datetime
from utils.functions import *
import json
import requests

def channelcheck(channelname, array):
    for item in array:
        if item in channelname:
            return 1

class OnMessage(commands.Cog):
    def __init__(self, client):
        self.bot = client

    async def mentionformat(self, arg, guild):
        list1 = arg.split(" ")
        for a in list1:
            a = str(a)
            a1 = a.replace('<', '').replace('>', '').replace('@', '').replace('!', '').replace('#', '').replace('&', '')
            try:
                a2 = int(a1)
            except:
                continue
            a3 = a1
            try:
                a1 = guild.get_member(a2)
                a3 = f"@{a1.name}#{a1.discriminator}"
            except:
                pass
            try:
                a1 = guild.get_role(a2)
                a3 = f"@{a1.name}"
            except:
                pass
            try:
                a1 = guild.get_channel(a2)
                a3 = f"#{a1.name}"
            except:
                pass
            try:
                for i in range(len(list1)):
                    if list1[i] == a:
                        try:
                            list1[i] = a3
                        except:
                            list1[i] = a1
                            pass
                    else:
                        pass
                arg = ' '.join(list1)
            except:
                pass
        return arg
                
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if not ctx.guild:
            return
        try:
            urllist = re.findall(r'(https?://[^\s]+)', ctx.content)
            positive_sites = []
            safe = False
            with open('utils/urls.json') as f:
                data = json.load(f)
            if urllist != []:
                for url in urllist:
                    try:
                        if "bit.ly" in url:
                            url = url.split("//")[1]
                            headers1 = {
                                'Authorization': 'Bearer a631792d290aee90423484eeafb05f86344b6473',
                                'Content-Type': 'application/json'}
                            expanddata = '{ "bitlink_id": "%s" }' % url
                            response1 = requests.post('https://api-ssl.bitly.com/v4/expand', headers=headers1, data=expanddata)
                            response2 = response1.json()
                            if response2.get("long_url") != None:
                                url = response2.get("long_url")
                    except:
                        pass
                    try:
                        spliturl = url.split(url.split("/")[3])[0]
                    except:
                        spliturl = url
                    for url1 in data["urls"]:
                        if url1 in ctx.content or spliturl in url1:
                            await ctx.delete()
                            return
                    for url1 in data["safeurls"]:
                        if url1 in ctx.content:
                            safe = True
                    if safe != True:
                        try:
                            params = {'apikey': '678e6935abfdd6df1776511b1024faaec5bd0636dd166b0276a398039dca6b79', 'url': url}
                            response = requests.post('https://www.virustotal.com/vtapi/v2/url/scan', data=params)
                            scan_id = response.json()['scan_id']
                            report_params = {'apikey': '678e6935abfdd6df1776511b1024faaec5bd0636dd166b0276a398039dca6b79', 'resource': scan_id}
                            report_response = requests.get('https://www.virustotal.com/vtapi/v2/url/report', params=report_params)
                            scans = report_response.json()['scans']
                            positive_sites = []
                            for key, value in scans.items():
                                if value['detected'] == True:
                                    positive_sites.append(key)
                        except:
                            pass
                        if positive_sites != []:
                            data["urls"].append(spliturl)
                            with open('utils/urls.json', 'w') as json_file:
                                json.dump(data, json_file)
                            try:
                                await ctx.delete()
                                return
                            except:
                                pass
                        else:
                            data["safeurls"].append(spliturl)
                            with open('utils/urls.json', 'w') as json_file:
                                json.dump(data, json_file)
        except:
            pass
        try:
            guilds = [814607392687390720, 380308776114454528, 841225582967783445, 380308776114454528, 820383461202329671, 789891385293537280]
            if ctx.guild.id in guilds:
                for channel in ctx.guild.channels:
                    if "zap" in channel.name:
                        zapchannel = channel.id
                highstaff = discord.utils.get(ctx.guild.roles, name = "Media Manager")
                zaprole = discord.utils.get(ctx.guild.roles, name = "Zap")
                author = discord.utils.get(ctx.guild.members, name = ctx.author.name)
                channelreq = False
                for item in ["announcements", "updates", "competitions", "events"]:
                    if item in ctx.channel.name:
                        channelreq = True
                        break
                if "youtube" in ctx.channel.name and ctx.channel.id != zapchannel:
                    if f"<@&{zaprole.id}>" in ctx.content and highstaff in ctx.author.roles:
                        channel = client.get_channel(zapchannel)
                        embedDescription  = (f"#{ctx.channel.name}\n𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁 𝗕𝘆: {ctx.author.name}#{ctx.author.discriminator}\n\n{await self.mentionformat(ctx.content, ctx.guild)}")
                        if ctx.attachments:
                            embedDescription  = f"#{ctx.channel.name}\n𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁 𝗕𝘆: {ctx.author.name}#{ctx.author.discriminator}\n\n{await self.mentionformat(ctx.content, ctx.guild)}\n\n{ctx.attachments[0].url}"
                        embed = addEmbed(ctx,None,embedDescription, None, False)
                        await sendwebhook(ctx, ctx.author.name, channel, None, [embed])
                elif ctx.webhook_id and channelreq and ctx.channel.id != zapchannel:
                    if "Ham5teak Bot 3.0" not in ctx.embeds[0].footer.text:
                        pass
                    elif f"<@&{zaprole.id}>" in ctx.embeds[0].description and highstaff in author.roles:
                        channel = client.get_channel(zapchannel)
                        embed = ctx.embeds[0]
                        if ctx.webhook_id:
                            author = author
                        else:
                            author = ctx.author
                        embedDescription  = f"#{ctx.channel.name}\n𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁 𝗕𝘆: {author.name}#{author.discriminator}\n\n{await self.mentionformat(embed.description, ctx.guild)}"
                        if embed.image.url:
                            embedDescription  = f"#{ctx.channel.name}\n𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁 𝗕𝘆: {author.name}#{author.discriminator}\n\n{await self.mentionformat(embed.description, ctx.guild)}\n\n{embed.image.url}"
                        embed.description = embedDescription
                        await sendwebhook(ctx, ctx.author.name, channel, None, [embed])
        except:
            pass
        try:
            channelnames = ["announcements", "updates", "competitions", "events"]
            if (ctx.guild.id in premium_guilds and ctx.channel.id in announcementschannels[ctx.guild.id]) or (ctx.guild.id not in premium_guilds and channelcheck(ctx.channel.name, channelnames)):
                if not ctx.author.bot:
                    await asyncio.sleep(2.5)
                    if ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!"):
                        return
                    else:
                        if ctx.attachments:
                            for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                                if imageextensions in ctx.attachments[0].filename:
                                    if str(ctx.guild.id) in str(betaannouncementguilds):
                                        await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️", 1)
                                    else:
                                        await attachmentAutoEmbed(ctx, 1, "announcement", "👍", "❤️", 0)
                                    return
                            await attachmentAutoEmbed(ctx, 0, "announcement", "👍", "❤️", 1)
                            return
                        if not ctx.attachments:
                            try:
                                await ctx.delete()
                            except:
                                pass
                            embedDescription  = (f"{ctx.content}")
                            embed = addEmbed(ctx,None,embedDescription, None, False)
                            sent = False
                            if str(ctx.guild.id) in str(betaannouncementguilds):
                                sent = await sendwebhook(ctx, ctx.author.name, ctx.channel, None, [embed])
                                while sent == True:
                                    await asyncio.sleep(2)
                                    msg = await ctx.channel.history(limit=1).flatten()
                                    msg = msg[0]
                                    try:
                                        [await msg.add_reaction(item) for item in ["👍", "❤️"] if item != None]
                                    except:
                                        pass
                                    sent = False
                            else:
                                msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                                try:
                                    [await msg.add_reaction(item) for item in ["👍", "❤️"] if item != None]
                                except:
                                    pass
                            print(f"An announcement was made in #{ctx.channel.name} by {ctx.author}.")
                    return
            if ((ctx.guild.id in premium_guilds and ctx.channel.id in suggestionchannels[ctx.guild.id]) or ("suggestions" in ctx.channel.name)) and (not ctx.author.bot and not ctx.content.startswith("-") and not ctx.content.startswith("?") and not ctx.content.startswith("!")):
                if ctx.attachments:
                    for imageextensions in [".jpg", ".jpeg", ".png", ".gif"]:
                        if imageextensions in ctx.attachments[0].filename:
                            await attachmentAutoEmbed(ctx, 1, "suggestion", "✅", "❌")
                            return
                    await attachmentAutoEmbed(ctx, 0, "suggestion", "✅", "❌")
                    return
                if not ctx.attachments:
                    try:
                        await ctx.delete()
                    except:
                        pass
                    embedDescription  = (f"{ctx.content}")
                    msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription ))
                    try:
                        [await msg.add_reaction(item) for item in ["✅", "❌"] if item != None]
                    except:
                        pass
                    print(f"A suggestion was made in #{ctx.channel.name} by {ctx.author}.")
                return
            if (ctx.guild.id in premium_guilds and ctx.channel.id in pollchannels[ctx.guild.id] and not ctx.author.bot) or (ctx.guild.id not in premium_guilds and "poll" in ctx.channel.name or "polls" in ctx.channel.name and not ctx.author.bot):
                if (ctx.content.startswith("-") or ctx.content.startswith("?") or ctx.content.startswith("!")) or (ctx.webhook_id or "poll-results" in ctx.channel.name):
                    return
                sent = True
                try:
                    await ctx.delete()
                except:
                    pass
                with open('utils/polls.json') as f:
                    data = json.load(f)
                components1 = []
                actionrows = []
                messageemojis = []
                reactionstotal = {}
                reactedusers = {}
                content = ctx.content.replace(":", '')
                content = e.demojize(content)
                regionalindicators = ['\U0001f1e6', '\U0001f1e7', '\U0001f1e8', '\U0001f1e9', '\U0001f1ea', '\U0001f1eb', '\U0001f1ec',
                 '\U0001f1ed', '\U0001f1ee', '\U0001f1ef', '\U0001f1f0', '\U0001f1f1', '\U0001f1f2', '\U0001f1f3', '\U0001f1f4', '\U0001f1f5',
                  '\U0001f1f6', '\U0001f1f7', '\U0001f1f8', '\U0001f1f9', '\U0001f1fa', '\U0001f1fc', '\U0001f1fd', '\U0001f1fe', '\U0001f1ff']
                for word in content.split(" "):
                    for em in re.findall(r'(:[^:]*:)', word):
                        messageemojis.append(em)
                    for reg in regionalindicators:
                        for emm in re.findall(rf'{reg}', word):
                            messageemojis.append(emm)
                for emoji in messageemojis:
                    try:
                        emoji1 = e.emojize(emoji)
                        components1.append(create_button(label="", style=ButtonStyle.gray, custom_id=f"{emoji1}-poll", emoji=emoji1))
                        reactionstotal.update({emoji1: 0})
                    except:  #nosec
                        pass
                components2 = [components1[n:n+5] for n in range(0, len(components1), 5)]
                [actionrows.append(create_actionrow(*row)) for row in components2]
                reactionstotal1 = str(reactionstotal).replace("{", "").replace("}", "").replace(", ", f"\n").replace(":", "").replace("'", "")
                embedDescription  = (f"{ctx.content}\n\n```\n{reactionstotal1}\n```")
                try:
                    if ctx.attachments:
                        await ctx.attachments[0].save(f"./{ctx.attachments[0].filename}")
                        file = discord.File(ctx.attachments[0].filename)
                        msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription, image=f"attachment://{ctx.attachments[0].filename}"), components=[*actionrows], file=file)
                    else:
                        msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription), components=[*actionrows])
                    reactedusers.update({msg.id: []})
                    endTime = datetime.datetime.now() + datetime.timedelta(hours=48)
                    data.update({msg.id: {}})
                    data[msg.id].update({"reactedusers": []})
                    data[msg.id].update({"time": endTime.strftime("%m/%d/%Y, %H:%M:%S")})
                    data[msg.id].update({"reactionstotal": reactionstotal})
                    with open('utils/polls.json', 'w') as json_file:
                        json.dump(data, json_file)
                except:
                    reactionstotal1 = str(reactionstotal).replace("{", "").replace("}", "").replace(", ", f"\n").replace(":", "").replace("'", "")
                    embedDescription  = (f"{ctx.content}\n\n```\n{reactionstotal1}\n```")
                    msg = await ctx.channel.send(embed=addEmbed(ctx,None,embedDescription), components=[])
                print(f"A poll was made in #{ctx.channel.name} by {ctx.author}.")
                return
            if "console-" in ctx.channel.name and "console-hambot" not in ctx.channel.name:
                messagestrip = await stripmessage(ctx.content, 'a server operator')
                if messagestrip:
                    print(messagestrip)
                    alertschannelcheck = selectquery(sql, 'guilds', 'alertschannel', f'guild_id = {ctx.guild.id}')
                    generalchannelcheck = selectquery(sql, 'guilds', 'generalchannel', f'guild_id = {ctx.guild.id}')
                    if alertschannelcheck != 0:
                        alertschannel = client.get_channel(alertschannelcheck)
                        msg = await alertschannel.send(content=f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!',
                        components=[create_actionrow(create_button(style=ButtonStyle.red, label="Verify"))])
                        if generalchannelcheck != 0:
                            generalchannel = client.get_channel(generalchannelcheck)
                            await generalchannel.send(content=f'**WARNING!** `/op` or `/deop` was used. Check {alertschannel.mention} for more info.', delete_after=600)
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
            if "console-" in ctx.channel.name and "console-hambot" not in ctx.channel.name:
                lptriggers = ["now inherits permissions from", "no longer inherits permissions from",
                "[LP] Set group.", "[LP] Web editor data was applied to user", "[LP] Web editor data was applied to group", "[LP] Promoting", "[LP] Demoting"]
                for trigger in lptriggers:
                    messagestrip = await stripmessage(ctx.content, trigger)
                    if messagestrip:
                        print(messagestrip)
                        lpalertschannelcheck = selectquery(sql, 'guilds', 'lpalertschannel', f'guild_id = {ctx.guild.id}')
                        if lpalertschannelcheck != 0:
                            lpalertschannel = client.get_channel(lpalertschannelcheck)
                            try:
                                await lpalertschannel.send(f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!')
                            except: #nosec
                                pass
            if ctx.guild.id in ham_guilds:
                if "console-" in ctx.channel.name and "console-hambot" not in ctx.channel.name:
                    lptriggers = ["issued server command: /sudo", "issued server command: /attachcommand",
                    "issued server command: /cmi attachcommand", "issued server command: /cmi sudo", 
                    "issued server command: /npc command add", "issued server command: /ic", "issued server command: /cmi ic",
                    "issued server command: /cmi:cmi sudo", "issued server command: /cmi:cmi attachcommand", "issued server command: /cmi:cmi ic"]
                    for trigger in lptriggers:
                        messagestrip = await stripmessage(ctx.content, trigger)
                        if messagestrip and "/icanhasbukkit" not in messagestrip:
                            print(messagestrip)
                            guildchannels = ctx.guild.channels
                            for channel in guildchannels:
                                if "command-alerts" in channel.name:
                                    await channel.send(f'```\n{messagestrip}\n```It originated from {ctx.channel.mention}!')
            if ctx.guild.id in ham_guilds:
                if "console-survival" in ctx.channel.name and "console-hambot" not in ctx.channel.name:
                    messagestrip = await stripmessage(ctx.content, '[HamAlerts] Thank you')
                    if messagestrip:
                        print(messagestrip)
                        guildchannels = ctx.guild.channels
                        for channel in guildchannels:
                            if "receipts" in channel.name:
                                await channel.send(f'```\n{messagestrip}\n```')
        except:
            return

def setup(client):
    client.add_cog(OnMessage(client))