import discord
from discord.ext import commands 
from luhn import *
from utils.functions import *

class SetCommandCog(commands.Cog):
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
                return
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setserver(self, ctx, serverip: str):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        try:
            server = MinecraftServer.lookup(serverip)
            status = server.status()
        except:
            embedDescription  = (f"Couldn't register {serverip} as server ip.")
            await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
            return
        guild_id = str(ctx.guild.id)
        where = (f"guild_id = {guild_id}")
        result = (insertquery(sql, 'guilds', 'mcserver', f"'{serverip}'", where))
        if (result == 0):
            embedDescription  = (f"Successfully registered {serverip} as server ip.")
            await ctx.channel.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
        else:
            embedDescription  = (f"Couldn't register {serverip} as server ip.")
            await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)

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
                return
        commandsloop2 = ["announcement", "poll", "suggestion"]
        for commanda in commandsloop2:
            try:
                if commanda == command:
                    try:
                        list11 = selectqueryall(sql, 'announcements', 'channel_id', f'guild_id = {ctx.guild.id}')
                        for item in list11:
                            if item == channel.id:
                                embedDescription  = (f"{channelid} is already registered.")
                                await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                                return
                    except:
                        pass
                    column = '(guild_id  , channel_id , channel_type)'
                    values = (guild_id , channelid , command)
                    result = (insertquery(sql, 'announcements', column , values, None))
                    if ctx.guild.id not in announcementschannels.keys() or ctx.guild.id not in suggestionchannels.keys() or ctx.guild.id not in pollchannels.keys():
                        announcementschannels[ctx.guild.id] = []
                    if command == "announcement":
                        announcementschannels[ctx.guild.id].append(channel.id)
                    elif command == "suggestion":
                        suggestionchannels[ctx.guild.id].append(channel.id)
                    elif command == "poll":
                        pollchannels[ctx.guild.id].append(channel.id)
                    if (result == 0):
                        embedDescription  = (f"Successfully registered {command} as `{channel.id}`")
                        await ctx.channel.send(embed=addEmbed(ctx,"green",embedDescription ), delete_after=5)
                    else:
                        embedDescription  = (f"Couldn't register {command} as {channelid}")
                        await ctx.channel.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                    return
            except Exception as e:
                print(e)

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
                return
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
                return
        embedDescription  =(f"Restriction type `{restrictname}` couldn't be removed.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return

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
                return
        embedDescription  =(f"Category `{categoryname}` couldn't be removed.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def removechannel(self, ctx, value: discord.TextChannel, channel):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), delete_after=5)
            return
        await deletemessage(ctx)
        categoryname = channel
        channelid = value.id
        channels = selectqueryall(sql, 'announcements', 'channel_id', f'channel_type = "{channel}"')
        for stralias in channels:
            if channelid == stralias[0]:
                if channel == "announcement":
                    announcementschannels[ctx.guild.id].remove(value.id)
                elif channel == "poll":
                    pollchannels[ctx.guild.id].remove(value.id)
                elif channel == "suggestion":
                    suggestionchannels[ctx.guild.id].remove(value.id)
                deletequery(sql, 'announcements', f"channel_id = {value.id} AND channel_type = '{channel}'")
                embedDescription  =(f"<#{value.id}> has been removed from `{categoryname}`.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
                return
        embedDescription  =(f"<#{value.id}> couldn't be removed from `{categoryname}`.")
        await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), delete_after=5)
        return
            
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

    @betaannouncements.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @setup.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)
        
    @removerestrict.error
    async def clear_error(self, ctx, error):
        await unknownerror(ctx, error)

    @setmove.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter a valid category id. `{getprefix2(ctx)}setmove <categoryid> <alias>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)
            
    @removemove.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please enter a valid category name. `{getprefix2(ctx)}removemove <categoryname>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @setchannel.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please specify the channel you would like to set. `{getprefix2(ctx)}setchannel <channel> <id>`', None), delete_after=5)
        else:
            await unknownerror(ctx, error)

    @setrestrict.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
                await deletemessage(ctx)
                await ctx.send(embed=addEmbed(None, "red", f'Please make sure to give all arguments correctly. `{getprefix2(ctx)}setrestrict <type> <role1> [role2] [role3]`', None), delete_after=5)
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
    client.add_cog(SetCommandCog(client))