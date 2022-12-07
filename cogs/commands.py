import aiohttp
import contextlib
import io
import textwrap
from traceback import format_exception
from luhn import *
from cardvalidator import luhn
import random
import string
import discord
from discord.ext import commands 
from dinteractions_Paginator import Paginator
from utils.functions import *
from mee6_py_api import API
from bs4 import BeautifulSoup
import requests
import re

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text
class CommandCog(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.command()
    async def rtfm(self, ctx, query: str, branch="stable"):
        try:
            if query == None:
                await ctx.send(embed=addEmbed(ctx, "invis", '`-rtfm <query> [branch]`'))
                return
            params = {"query": query, "location": f'https://discordpy.readthedocs.io/en/{branch}'}
            async with aiohttp.ClientSession() as session:
                response = await session.get(f'https://idevision.net/api/public/rtfm', params=params)
                data = await response.json()
                nodes = data["nodes"]
                if nodes == {}:
                    await ctx.send(embed=addEmbed(ctx, "invis", '**No Results**'))
                    return
            attributes = []
            attributeshref = []
            methods = []
            methodshref = []
            att = list(nodes.keys())[0].split('.')[-1].lower()
            if query.lower() == "user" or query == "discord.User":
                att = "id8"
            url_to_scrape = f"https://discordpy.readthedocs.io/en/{branch}/api.html#{list(nodes.keys())[0]}"
            html_document = getHTMLdocument(url_to_scrape)
            soup = BeautifulSoup(html_document, 'html.parser')
            for link in soup.find_all('section', attrs={'id': att}):
                link = str(link)
                for item in link.split('\n'):
                    if 'class="py-attribute-table-entry"' in item and '<a class="reference internal"' in item and "href=" in item and "span" not in item:
                        attributes.append(item.split(">")[1].split("<")[0])
                        attributeshref.append(item.split('href="')[1].split('"')[0])
                    elif 'class="py-attribute-table-entry"' in item and '<a class="reference internal"' in item and "href=" in item and "span" in item:
                        methods.append(item.split('href="')[1].split('"')[0].split('.')[2])
                        methodshref.append(item.split('href="')[1].split('"')[0])
            mainembed = addEmbed(ctx, "invis", '\n'.join([f'__[{key}]({value})__' for key,value in nodes.items()]))
            values1 = []
            values2 = []
            removed1 = 0
            removed2 = 0
            for i in range(len(attributes)):
                values1.append(f"[{attributes[i]}](https://discordpy.readthedocs.io/en/{branch}/api.html{attributeshref[i]})")
            for i in range(len(methods)):
                values2.append(f"[{methods[i]}](https://discordpy.readthedocs.io/en/{branch}/api.html{methodshref[i]})")
            while len('\n'.join(values1)) > 1000:
                values1 = values1[:-1]
                removed1 += 1
            while len('\n'.join(values2)) > 1000:
                values2 = values2[:-1]
                removed2 += 1
            values1l = '\n'.join(values1)
            values2l = '\n'.join(values2)
            if values1 != []:
                try:
                    if removed1 != 0:
                        mainembed.add_field(name="**Attributes**", value=f"{values1l}\n**... {removed1} more**", inline=True)
                    else:
                        mainembed.add_field(name="**Attributes**", value=f"{values1l}", inline=True)
                except:
                    pass
            if values2 != []:
                try:
                    if removed2 != 0:
                        mainembed.add_field(name="**Methods**", value=f"{values2l}\n**... {removed2} more**", inline=True)
                    else:
                        mainembed.add_field(name="**Methods**", value=f"{values2l}", inline=True)
                except:
                    pass
            await ctx.send(embed=mainembed)
        except Exception as exc:
            print(exc)

    @commands.command()
    async def ping(self, ctx):
        await deletemessage(ctx)
        latency = int(client.latency * 1000)
        await ctx.send(embed=addEmbed(ctx, "dark_teal", f"Bot Latency: `{latency}ms`"), delete_after=5)
        return

    @commands.command()
    @commands.check(is_owner)
    async def reload(self, ctx, cog:str):
        await deletemessage(ctx)
        if cog == "all":
            for cog2 in os.listdir('./cogs'):
                if cog2.endswith('.py'):
                    cog1 = cog2[:-3]
                    try:
                        self.bot.unload_extension(f"cogs.{cog1}")
                        self.bot.load_extension(f"cogs.{cog1}")
                        print(f"{cog1} has successfully been reloaded!")
                    except Exception as e:
                        print(e)
                        return
            for cog2 in os.listdir('./cogs/games'):
                if cog2.endswith('.py'):
                    cog1 = cog2[:-3]
                    try:
                        self.bot.unload_extension(f"cogs.games.{cog1}")
                        self.bot.load_extension(f"cogs.games.{cog1}")
                        print(f"{cog1} has successfully been reloaded!")
                    except Exception as e:
                        print(e)
                        return
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"All cogs have successfully been reloaded!"), delete_after=7)
            return
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            print(f"{cog} has successfully been reloaded!")
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"`{cog}` has successfully been reloaded!"), delete_after=7)
            return
        except Exception as e:
            print(e)

    @commands.command()
    @commands.check(is_owner)
    async def load(self, ctx, cog:str):
        await deletemessage(ctx)
        try:
            self.bot.load_extension(f"cogs.{cog}")
            print(f"{cog} has successfully been loaded!")
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"`{cog}` has successfully been loaded!"), delete_after=7)
        except Exception as e:
            print(e)
        return
            
    @commands.command()
    @commands.check(is_owner)
    async def unload(self, ctx, cog:str):
        await deletemessage(ctx)
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            print(f"{cog} has successfully been unloaded!")
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"`{cog}` has successfully been unloaded!"), delete_after=7)
        except Exception as e:
            print(e)
        return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        await ctx.channel.purge(limit=amount)
        embedDescription  = (f"{amount} messages were successfully deleted.")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=1)
        return

    @commands.command()
    @discord.ext.commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def generate(self, ctx):
        if ctx.channel != client.get_channel(1043427382083719178):
            return
        password = '' #nosec
        stringpunc = string.punctuation.replace("'", "").replace('"', '').replace('`', '')
        await deletemessage(ctx)
        for x in range (0,4):
            Password = random.choice(string.digits) #nosec
        for y in range(8): #nosec
            password = password + random.choice(string.digits)
        check = selectqueryall(sql, f'passwords', 'password', None)
        for pass1 in check:
            if pass1 == password:
                return await generate(ctx)
        result = insertquery(sql, f'passwords', '(password, used)', (password, 0), None)
        if result != 1:
            cc = luhn.generate(16)
            embedDescription  = (f"**Generated Password:** `{cc}{password}`")
        else:
            embedDescription  = (f"Password generation failed.")
        await ctx.send(embed=addEmbed(None, "aqua", embedDescription))
        return

    @commands.command()
    async def edit(self, ctx, id, *, embedDescription):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        msg = await ctx.channel.fetch_message(id)
        embedobj = msg.embeds[0]
        if msg.author.id != client.user.id:
            await deletemessage(ctx)
            webhook1 = await getwebhook(ctx, "Ham5teakBot3")
            async with aiohttp.ClientSession() as session:
                webh = discord.Webhook.from_url(webhook1.url, adapter=discord.AsyncWebhookAdapter(session=session))
                try:
                    imageurl = (embedobj.image.url).split("/")[6]
                    await webh.edit_message(id, embeds=[addEmbed(ctx, None, embedDescription, f"attachment://{imageurl}", False)])
                except:
                    await webh.edit_message(id, embeds=[addEmbed(ctx, None, embedDescription, None, False)])
            return
        await deletemessage(ctx)
        try:
            imageurl = (embedobj.image.url).split("/")[6]
            await ctx.channel.get_partial_message(id).edit(embed = addEmbed(ctx, None, embedDescription, f"attachment://{imageurl}"))
        except:
            await ctx.channel.get_partial_message(id).edit(embed = addEmbed(ctx, None, embedDescription, None))
        return

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx):
        await deletemessage(ctx)
        prefix = prefixes[f"{ctx.guild.id}"]
        await ctx.send(embed=addEmbed(ctx, None, f"Bot Prefix: `{prefix}`"), delete_after=5)  
        return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def move(self, ctx, alias):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        aliaslist = selectqueryall(sql, "categories", "category_name", f"guild_id = {ctx.guild.id}")
        for stralias in aliaslist:
            if alias == stralias[0]:
                ctxchannel = ctx.channel
                result = selectquery(sql, "categories", "category_id", f"category_name = '{alias}' AND guild_id = {ctx.guild.id}")
                cat = client.get_channel(result)
                await ctxchannel.edit(category=cat)
                embedDescription  = (f"{ctxchannel.mention} has been moved to category {alias}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
        return

    @commands.command(aliases=['rl'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def restrictlist(self, ctx):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        types = [selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')]
        for type in types:
            if types == 0:
                await ctx.send(embed=await nopermission(ctx), delete_after=5)
                return
            type1 = str(type).replace('(', '').replace(')', '').replace('(', '').replace("'", '').replace("[", '').replace("]", '').replace(',', '').replace(' ', f'\n')
            embedDescription  = (f"__**Restriction types you can use:**__\n{type1}")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), delete_after=10)
        return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def restrict(self, ctx, alias):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        if alias.lower() == "none":
            await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)
            embedDescription  = (f"{ctx.channel.mention} has been opened to public.")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
        aliaslist = selectqueryall(sql, f"restrict", "restrictrole_name", f"guild_id = {ctx.guild.id}")
        for stralias in aliaslist:
            if alias == stralias[0]:
                ctxchannel = ctx.channel
                sql.connect()
                result = selectquery(sql, f"restrict", "restrictrole3_id", f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                if result is None:
                    result1 = selectquery(sql, f'restrict', 'restrictrole2_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                    if result1 is None:
                        result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                        role = ctx.guild.get_role(result2)
                        overwrites1= {}
                        overwrites1.update({role: discord.PermissionOverwrite(view_channel=True),
                        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
                        for key in ctx.channel.overwrites.keys():
                            if isinstance(key, discord.Member):
                                overwrites1.update({key: ctx.channel.overwrites[key]})
                        await ctx.channel.edit(overwrites=overwrites1)
                        embedDescription  = (f"{ctxchannel.mention} has been restricted to {role.mention}")
                        await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
                        return
                    result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                    cat = ctx.guild.get_role(result1)
                    cat2 = ctx.guild.get_role(result2)
                    overwrites2 = {}
                    overwrites2.update({cat: discord.PermissionOverwrite(view_channel=True), cat2: discord.PermissionOverwrite(view_channel=True),
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
                    for key in ctx.channel.overwrites.keys():
                        if isinstance(key, discord.Member):
                            overwrites2.update({key: ctx.channel.overwrites[key]})
                    await ctx.channel.edit(overwrites=overwrites2)
                    embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention} and {cat2.mention}")
                    await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
                    return
                result2 = selectquery(sql, f'restrict', 'restrictrole_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                result3 = selectquery(sql, f'restrict', 'restrictrole2_id', f"restrictrole_name = '{alias}' AND guild_id = {ctx.guild.id}")
                cat = ctx.guild.get_role(result)
                cat2 = ctx.guild.get_role(result2)
                cat3 = ctx.guild.get_role(result3)
                overwrites3 = {}
                overwrites3.update({cat: discord.PermissionOverwrite(view_channel=True), cat2: discord.PermissionOverwrite(view_channel=True),
                cat3: discord.PermissionOverwrite(view_channel=True), ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
                for key in ctx.channel.overwrites.keys():
                    if isinstance(key, discord.Member):
                        overwrites3.update({key: ctx.channel.overwrites[key]})
                await ctx.channel.edit(overwrites=overwrites3)
                embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention}, {cat2.mention} and {cat3.mention}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
        return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def demanded(self, ctx, messageid):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        result = selectquery(sql, 'guilds', 'demandedsuggestions', f'guild_id = {ctx.guild.id}')
        if result == 0:
            embedDescription  = (f"This server doesn't have a demanded suggestions channel set.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), delete_after=5)
        else:
            msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
            for reaction in msg.reactions:
                if reaction.emoji != "✅":
                    pass 
                else:
                    reactiona = reaction
                    dsuggestionschannel = client.get_channel(result)
                    finalcount = int(reactiona.count - 1)
                    embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                    embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                    embed2 = msg.embeds[0]
                    await sendwebhook(ctx, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                    embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully demanded!")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
                    return
        return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reject(self, ctx, messageid):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        result = selectquery(sql, 'guilds', 'rejectedsuggestions', f'guild_id = {ctx.guild.id}')
        if result == 0:
            embedDescription  = (f"This server doesn't have a rejected suggestions channel set.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), delete_after=5)
        else:
            msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
            for reaction in msg.reactions:
                if reaction.emoji != "❌":
                    pass
                else:
                    reactiona = reaction
                    rsuggestionschannel = client.get_channel(result)
                    finalcount = int(reactiona.count - 1)
                    embedDescription  = (f"**{finalcount} Downvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                    embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                    embed2 = msg.embeds[0]
                    await sendwebhook(ctx, "Rejected Suggestions", rsuggestionschannel, None, [embed1, embed2])
                    embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully rejected!")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
                    return
        return

    @commands.command(aliases=['level', 'levelup', 'lvl', 'lvlup'])
    @commands.cooldown(3, 90, commands.BucketType.guild)
    async def rank(self, ctx):
        mee6API = API(380308776114454528)
        if ctx.guild.id != 380308776114454528:
            return
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        await deletemessage(ctx)
        await ctx.send(embed=addEmbed(ctx, None, f"This action may take a few seconds so please be patient."), delete_after=5)
        nitrorole = ctx.guild.get_role(585709169521459212) # Nitro booster role
        premiumrole = ctx.guild.get_role(803054503817248768) # Premium member role
        if nitrorole in ctx.author.roles or premiumrole in ctx.author.roles or moderatorcheck1 != 0:
            level10role = ctx.guild.get_role(853371968601325630) # Level 10 role
            level20role = ctx.guild.get_role(853371990790635550) # Level 20 role
            level30role = ctx.guild.get_role(853372011216633876) # Level 30 role
            level40role = ctx.guild.get_role(853372025303990292) # Level 40 role
            level50role = ctx.guild.get_role(853372040690401321) # Level 50 role
            level60role = ctx.guild.get_role(853372065717157902) # Level 60 role
            roles = {"10": level10role, "20": level20role,"30": level30role,
            "40": level40role,"50": level50role,"60": level60role}
            userlevel = await mee6API.levels.get_user_level(ctx.author.id)
            if userlevel >= 10 and userlevel < 20 and roles[f"10"] not in ctx.author.roles:
                await ctx.author.add_roles(roles[f"10"])
                await ctx.send(embed=addEmbed(ctx, None, f"You have successfully been given the role {roles[f'10']}."), delete_after=5)
            levels = [20, 30, 40, 50, 60]
            for level1 in levels:
                if userlevel >= level1 and userlevel < int(level1 + 10) and roles[f"{int(level1)}"] not in ctx.author.roles:
                    if roles[f"{int(level1 - 10)}"] in ctx.author.roles:
                        await ctx.author.remove_roles(roles[f"{int(level1 - 10)}"])
                    await ctx.author.add_roles(roles[f"{int(level1)}"])
                    await ctx.send(embed=addEmbed(ctx, None, f"You have successfully been given the role {roles[f'{int(level1)}'].mention}."), delete_after=5)
        else:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        return
            
    @commands.command(aliases=['ml'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def movelist(self, ctx):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5) 
            return
        await deletemessage(ctx)
        categories = [selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')]
        for category in categories:
            if categories == 0:
                await ctx.send(embed=await nopermission(ctx), delete_after=5)
                return
            newcat = str(category).replace('(', '').replace(')', '').replace('(', '').replace("'", '').replace("[", '').replace("]", '').replace(',', '').replace(' ', f'\n')
            embedDescription  = (f"__**Categories you can move channels to:**__\n{newcat}")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=10)
        return   
            
    @commands.command(aliases=['cl'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channellist(self, ctx):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5) 
            return
        await deletemessage(ctx)
        message = "**Announcement Channels:**"
        try:
            achannels = selectqueryall(sql, 'announcements', 'channel_id', f'guild_id = {ctx.guild.id} AND channel_type = "announcement"')
            if achannels == 0:
                await ctx.send(embed=await nopermission(ctx), delete_after=5)
                return
            for achannel in achannels:
                message += f" - <#{achannel[0]}>"
        except:
            message += "\n-\n"
        message += "\n\n"
        message += "**Suggestion Channels:**"
        try:
            schannels = selectqueryall(sql, 'announcements', 'channel_id', f'guild_id = {ctx.guild.id} AND channel_type = "suggestion"')
            if schannels == 0:
                await ctx.send(embed=await nopermission(ctx), delete_after=5)
                return
            for schannel in schannels:
                message += f" - <#{schannel[0]}>"
        except:
            message += "\n-\n"
        message += "\n\n"
        message += "**Poll Channels:**"
        try:
            pchannels = selectqueryall(sql, 'announcements', 'channel_id', f'guild_id = {ctx.guild.id} AND channel_type = "poll"')
            if pchannels == 0:
                await ctx.send(embed=await nopermission(ctx), delete_after=5)
                return
            for pchannel in pchannels:
                message += f" - <#{pchannel[0]}>"
        except:
            message += "\n-\n"
        await ctx.send(embed=addEmbed(ctx,"dark_teal",message ), delete_after=20)
        return

    @commands.command(aliases=['eval', 'e'])
    @commands.check(is_owner)
    async def evaluate(self, ctx, *, code):
        if code is None:
            return
        pages = []
        paginationList = []
        code = clean_code(code)
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": client,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec( # nosec
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                if obj is not None:
                    result = f"{stdout.getvalue()}\n-- {obj}\n"
                else:
                    result = f"{stdout.getvalue()}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))
        pages1 = [result[i:i+4080] for i in range(0, len(result), 4080)]
        embedpages = list(map(lambda x: addEmbed(ctx, None, f"```py\n{x}\n```"), pages1))
        embedpages = list(map(lambda x: settitle(x, f"Page: {embedpages.index(x) + 1}"), embedpages))
        if len(embedpages) > 1:
            await Paginator(bot=client, ctx=ctx, pages=embedpages, useButtons=False)
        else:
            await ctx.send(embed=addEmbed(ctx, "invis", f"```py\n{result}\n```"))
        return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.errors.CommandNotFound):
            return
        else:
            pass

    @evaluate.error
    async def clear_error(self, ctx, error):
        await ctx.send(embed=addEmbed(None, "invis", f'```py\n{error}\n```'))

    @move.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter the command correctly. `{getprefix2(ctx)}move <category>`'), delete_after=5)
        elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter a valid category. `{getprefix2(ctx)}move <category>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @ping.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @reload.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter a valid cog name. `{getprefix2(ctx)}reload <cog/all>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)
        
    @unload.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter a valid cog name. `{getprefix2(ctx)}unload <cog>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)
        
    @movelist.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @restrictlist.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
                
    @reject.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @demanded.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @generate.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @rank.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=addEmbed(ctx, None, f"This command is on global cooldown for {error.retry_after:.2f} seconds."))
        else:
            await unknownerror(ctx, error)

    @edit.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please specify the id of the message you would like to edit. `{getprefix2(ctx)}edit <messageid> <newmessage>`'), delete_after=5)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=addEmbed(None, "red", 'Please enter a valid message ID.', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @purge.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.BadArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please make sure to enter a number. `{getprefix2(ctx)}purge <amount>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @restrict.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
                await deletemessage(ctx)
                await ctx.send(embed=addEmbed(None, "red", f'Please specify the restrict type you would like to apply. `{getprefix2(ctx)}restrict <type> <user>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

def setup(client):
    client.add_cog(CommandCog(client))