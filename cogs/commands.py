import aiohttp
import contextlib
import io
import textwrap
from traceback import format_exception
from luhn import *
from pygicord import Paginator
from cardvalidator import luhn
import random
import string
import discord
from discord.ext import commands 
from cogs.functions import *

class CommandCog(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def setprefix(self, ctx, prefix = None):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        if prefix is None:
            embedDescription  = (f"Please provide all required arguments. `-setprefix <prefix>`.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return
        if len(prefix) >= 6:
            embedDescription  = (f"{prefix} has too many characters for a prefix.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return
        if ctx.guild.id in premium_guilds:
            insertquery(sql, "guilds", "prefix", f"'{prefix}'", f"guild_id = {ctx.guild.id}")
            prefixes[f"{ctx.guild.id}"] = prefix
        elif ctx.guild.id not in premium_guilds:
            prefixes[f"{ctx.guild.id}"] = prefix
        else: 
            return
        embedDescription  = (f"Prefix succesfully set to `{prefix}`")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)

    @commands.command()
    async def ping(self, ctx):
        await deletemessage(ctx)
        latency = int(client.latency * 1000)
        await ctx.send(embed=addEmbed(ctx, "dark_teal", f"Bot Latency: `{latency}ms`"), delete_after=5)

    @commands.command()
    @commands.check(is_owner)
    async def reload(self, ctx, cog:str):
        await deletemessage(ctx)
        if cog == "all":
            cogs = ["commands","functions","on_guild_channel_create","on_reaction_add","slashcommands","on_message"]
            for cog1 in cogs:
                try:
                    self.bot.unload_extension(f"cogs.{cog1}")
                    self.bot.load_extension(f"cogs.{cog1}")
                except Exception as e:
                    print(e)
                    return
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"All cogs have successfully been reloaded!"), delete_after=7)
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(embed=addEmbed(ctx, "dark_teal", f"`{cog}` has successfully been reloaded!"), delete_after=7)
        except Exception as e:
            print(e)

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

    @commands.command()
    @discord.ext.commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def setup(self, ctx, password, admin_role_id:discord.Role, mod_role_id:discord.Role):
        await deletemessage(ctx)
        async def invalidpass():
            embedDescription  = (f"Invalid password.")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), delete_after=5)
        cc = password[:16]
        password = password[16:].strip()
        if verify(cc) == False:
            print("cc fail")
            await invalidpass()
            return
        elif verify(cc) == True:
            check = selectqueryall(sql, f'passwords', 'password', None)
            found = False
            for pass1 in check:
                if pass1[0] == password:
                    found = True
            if found != True:
                print("pass doesn't exist")
                await invalidpass()
                return
            check2 = selectquery(sql, f'passwords', 'used', f"password = '{password}'")
            if check2 == 1:
                embedDescription  = (f"This password was already used.")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ))
                return
            elif check2 == 0:
                insertquery(sql, f'passwords', 'used', '(1)', f'password = "{str(password)}"')
                insertquery(sql, f'passwords', 'guild_id', f'{ctx.guild.id}', f'password = "{str(password)}"')
        guild_id = ctx.guild.id
        if guild_id in premium_guilds:
            embedDescription  = (f"You are already Logged in as Premium")
            await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ))
            return
        else:
            guild_name = ctx.guild.name
            column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
            values = (guild_id , guild_name , True , admin_role_id.id , mod_role_id.id)
            where = None
            result = (insertquery(sql, 'guilds' , column , values, where))
            premium_guilds.append(ctx.guild.id)
            if result == 0:
                embedDescription  = (f"Registered successfully")
                await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
            else:
                embedDescription  = (f"Register Failed")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)

    @commands.command()
    @discord.ext.commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def generate(self, ctx):
        if ctx.channel != client.get_channel(850260644322344960):
            return
        password = ''
        stringpunc = string.punctuation.replace("'", "").replace('"', '').replace('`', '')
        await deletemessage(ctx)
        for x in range (0,4):
            Password = random.choice(string.digits)
        for y in range(8):
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

    @commands.command()
    @discord.ext.commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setrestrict(self, ctx, alias ,role1:discord.Role, role2:discord.Role = None, role3:discord.Role = None):
        await deletemessage(ctx)
        guild_id = ctx.guild.id
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        if guild_id not in premium_guilds:
            embedDescription  = (f"You premium to use this command.")
            await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ), delete_after=5)
            return
        restricttypes = selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')
        for stralias in restricttypes:
            if alias == stralias[0]:
                embedDescription  =(f"Restrict type `{alias}` already exists.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return 1
        else:
            if role3 is None:
                if role2 is None:
                    column = '(guild_id  , restrictrole_name , restrictrole_id)'
                    values = (guild_id , alias , role1.id)
                    where = None
                    result = (insertquery(sql, f'restrict' , column , values, where))
                    sql.connect()
                    querycursor = sql.cursor()
                    sql.commit()
                    querycursor.close()        
                    if (result == 0):
                        embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention}")
                        await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
                    else:
                        embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention}")
                        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                    return
                column = '(guild_id  , restrictrole_name , restrictrole_id , restrictrole2_id)'
                values = (guild_id , alias , role1.id , role2.id)
                where = None
                result = (insertquery(sql, f'restrict' , column , values, where))
                sql.connect()
                querycursor = sql.cursor()
                sql.commit()
                querycursor.close()        
                if (result == 0):
                    embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention} and {role2.mention}")
                    await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
                else:
                    embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention} and {role2.mention}")
                    await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return
            column = '(guild_id  , restrictrole_name , restrictrole_id , restrictrole2_id, restrictrole3_id)'
            values = (guild_id , alias , role1.id , role2.id, role3.id)
            where = None
            result = (insertquery(sql, f'restrict' , column , values, where))
            sql.connect()
            querycursor = sql.cursor()
            sql.commit()
            querycursor.close()        
            if (result == 0):
                embedDescription  = (f"Restrict `{alias}` successfully set as {role1.mention}, {role2.mention} and {role3.mention}")
                await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
            else:
                embedDescription  = (f"Restrict `{alias}` failed to set as {role1.mention}, {role2.mention} and {role3.mention}")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
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
            webhook1 = await getwebhook(self, ctx, "Ham5teakBot3")
            async with aiohttp.ClientSession() as session:
                webh = discord.Webhook.from_url(webhook1.url, adapter=discord.AsyncWebhookAdapter(session=session))
                await webh.edit_message(id, embeds=[addEmbed2(ctx, None, embedDescription, embedobj.image.url)])
            return
        await deletemessage(ctx)
        await ctx.channel.get_partial_message(id).edit(embed = addEmbed(ctx, None, embedDescription, embedobj.image.url))

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx):
        await deletemessage(ctx)
        prefix = prefixes[f"{ctx.guild.id}"]
        await ctx.send(embed=addEmbed(ctx, None, f"Bot Prefix: `{prefix}`"), delete_after=5)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setchannel(self, ctx, command, channel: discord.TextChannel):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        guild_id = ctx.guild.id
        channelid = str(channel.id)
        commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
        , "rejectedsuggestions", "acceptedsuggestions", "demandedsuggestions"]
        for commanda in commandsloop:
            if commanda == command:
                column = (command)
                values = (channelid)
                where = (f"guild_id = {guild_id}")
                result = (insertquery(sql, 'guilds', column , values, where))
                if (result == 0):
                    embedDescription  = (f"Successfully registered {command} as `{channel.id}`")
                    await ctx.channel.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
                else:
                    embedDescription  = (f"Couldn't register {command} as {channelid}")
                    await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)     

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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def restrict(self, ctx, alias, user:discord.User):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        if alias.lower() == "none":
            await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)
            embedDescription  = (f"{ctx.channel.mention} has been opened to public.")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
        tickettool = ctx.guild.get_member(557628352828014614)
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
                        overwrites1.update({user: discord.PermissionOverwrite(view_channel=True)})
                        if tickettool is not None:
                            overwrites1.update({tickettool: discord.PermissionOverwrite(view_channel=True)})
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
                    overwrites2.update({user: discord.PermissionOverwrite(view_channel=True)})
                    if tickettool is not None:
                        overwrites2.update({tickettool: discord.PermissionOverwrite(view_channel=True)})
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
                overwrites3.update({user: discord.PermissionOverwrite(view_channel=True)})
                if tickettool is not None:
                    overwrites3.update({tickettool: discord.PermissionOverwrite(view_channel=True)})
                await ctx.channel.edit(overwrites=overwrites3)
                embedDescription  = (f"{ctxchannel.mention} has been restricted to {cat.mention}, {cat2.mention} and {cat3.mention}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def setmove(self, ctx, categoryi: discord.CategoryChannel, alias):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        movecheck = selectquery(sql, 'guilds', 'custommovecount', f'guild_id = {ctx.guild.id}')
        if movecheck >= 45:
            await ctx.send(embed=addEmbed(ctx, None, f"Guild has {movecheck} custommoves set which is over the limit."), delete_after=5)
            return
        await deletemessage(ctx)
        guild_id = ctx.guild.id
        categoryid = str(categoryi.id)
        categoryname = str(alias).replace('"', '').replace("'", "")
        if guild_id not in premium_guilds:
            embedDescription  = (f"You need premium to use this command.")
            await ctx.send(embed=addEmbed(ctx,"blue",embedDescription ))
            return
        categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
        for stralias in categoryn:
            if categoryname == stralias[0]:
                embedDescription  =(f"Category `{categoryname}` already exists.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return 1
        column = '(guild_id, category_name)'
        values = (guild_id, categoryname)
        where = None
        result = (insertquery(sql, 'categories', column , values, where))
        column = ('category_id')
        values = (f"'{categoryid}'")
        where = (f"category_name = '{categoryname}'")
        result = (insertquery(sql, 'categories', column , values, where))
        if (result == 0):
            embedDescription =(f"Successfully registered {categoryname} as `{categoryid}`")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), delete_after=5)
            insertquery(sql, 'guilds', 'custommovecount', f'{len(categoryn) + 1}', f'guild_id = {ctx.guild.id}')
        else:
            embedDescription  =(f"Couldn't register {categoryname} as `{categoryid}`")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def removerestrict(self, ctx, alias):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        restrictname = alias
        restrictlist = selectqueryall(sql, f'restrict', 'restrictrole_name', f'guild_id = {ctx.guild.id}')
        for stralias in restrictlist:
            if restrictname == stralias[0]:
                deletequery(sql, f'restrict', f"restrictrole_name = '{restrictname}'")
                embedDescription  =(f"Restriction type `{restrictname}` has been removed.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return 1
        embedDescription  =(f"Restriction type `{restrictname}` couldn't be removed.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return 1

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def removemove(self, ctx, alias):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        categoryname = alias
        categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
        for stralias in categoryn:
            if categoryname == stralias[0]:
                categoryn = deletequery(sql, 'categories', f"category_name = '{categoryname}'")
                embedDescription  =(f"Category `{categoryname}` has been removed.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return 1
        embedDescription  =(f"Category `{categoryname}` couldn't be removed.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return 1

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
                    await sendwebhook(self, ctx, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                    embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully demanded!")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
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
                    await sendwebhook(self, ctx, "Rejected Suggestions", rsuggestionschannel, None, [embed1, embed2])
                    embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully rejected!")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5)
                    return
        
    @commands.command(aliases=['scc'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def simchannelcreate(self, ctx):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)

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

    @commands.command(aliases=['eval', 'e'])
    @commands.check(is_owner)
    async def evaluate(self, ctx, *, code):
        if code is None:
            return
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
        pages1 = [result[i:i+2000] for i in range(0, len(result), 2000)]
        if len(pages1) > 1:
            pages = []
            for page in pages1:
                pages.append(addEmbed(ctx, "invis", f"```py\n{page}\n```"))
            paginator = Paginator(pages=pages, timeout=6000)
            await paginator.start(ctx)
        else:
            await ctx.send(embed=addEmbed(ctx, "invis", f"```py\n{result}\n```"))
            
    @commands.command(aliases=['ba'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def betaannouncements(self, ctx, bool:bool):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5) 
            return
        await deletemessage(ctx)
        if bool == True:
            insertquery(sql, 'guilds', 'betaannouncements', ('1'), f'guild_id = {ctx.guild.id}')
            betaannouncementguilds.append(ctx.guild.id)
        if bool == False:
            insertquery(sql, 'guilds', 'betaannouncements', ('0'), f'guild_id = {ctx.guild.id}')
            betaannouncementguilds.remove(ctx.guild.id)
        embedDescription  = (f"Beta-Announcements have successfully been set to `{bool}`.")
        await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription ), delete_after=5) 

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.errors.CommandNotFound):
            return
        print(error)

    @evaluate.error
    async def clear_error(ctx, error):
        await ctx.send(embed=addEmbed2(ctx, "invis", f'```py\n{error}\n```'))

    @move.error
    async def clear_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter the command correctly. `{getprefix2(ctx)}move <category>`'), delete_after=5)
        elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category. `{getprefix2(ctx)}move <category>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @ping.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @reload.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid cog name. `{getprefix2(ctx)}reload <cog/all>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @betaannouncements.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @movelist.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @restrictlist.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @setup.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @removerestrict.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @generate.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)

    @setmove.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category id. `{getprefix2(ctx)}setmove <categoryid> <alias>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)
            
    @removemove.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please enter a valid category name. `{getprefix2(ctx)}removemove <categoryname>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @edit.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the id of the message you would like to edit. `{getprefix2(ctx)}edit <messageid> <newmessage>`'), delete_after=5)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=addEmbed2(ctx, "red", 'Please enter a valid message ID.', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @setchannel.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the channel you would like to set. `{getprefix2(ctx)}setchannel <channel> <id>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @purge.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.BadArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please make sure to enter a number. `{getprefix2(ctx)}purge <amount>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @restrict.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
                await deletemessage(ctx)
                await ctx.send(embed=addEmbed2(ctx, "red", f'Please specify the restrict type you would like to apply. `{getprefix2(ctx)}restrict <type> <user>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @setrestrict.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
                await deletemessage(ctx)
                await ctx.send(embed=addEmbed2(ctx, "red", f'Please make sure to give all arguments correctly. `{getprefix2(ctx)}setrestrict <type> <role1> [role2] [role3]`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)
        
    @setprefix.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
                await deletemessage(ctx)
                await ctx.send(f'Please specify the prefix you would like to apply. `{getprefix2(ctx)}setprefix <prefix>`', delete_after=5)
        else:
            await unknownerror(ctx, error)

def setup(client):
    client.add_cog(CommandCog(client))