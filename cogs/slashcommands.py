import discord
from discord.ext import commands
from discord_slash import cog_ext
import aiohttp
import aiofiles
import os
from luhn import *
from utils.functions import *

class Slash(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @cog_ext.cog_slash(name="accept")
    async def accept(self, ctx, messageid):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        result = selectquery(sql, 'guilds', 'acceptedsuggestions', f'guild_id = {ctx.guild.id}')
        if result == 0:
            embedDescription  = (f"This server doesn't have an accepted suggestions channel set.")
            await ctx.send(embed=addEmbed(ctx,discord.Color.teal,embedDescription ), hidden=True)
        else:
            msg = await ctx.guild.get_channel(ctx.channel.id).fetch_message(messageid)
            for reaction in msg.reactions:
                if reaction.emoji != "✅":
                    return 
                else:
                    reactiona = reaction
                    aschannel = client.get_channel(result)
                    finalcount = int(reactiona.count - 1)
                    embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {ctx.channel.mention}")
                    embed1 = addEmbed(ctx,"dark_teal",embedDescription)
                    embed2 = msg.embeds[0]
                    await sendwebhook(ctx, "Accepted Suggestions", aschannel, None, [embed1, embed2])
                    embedDescription  = (f"[Suggestion]({msg.jump_url}) successfully accepted!")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), hidden=True)
                    return

    @cog_ext.cog_slash(name="status", description="View minecraft network status")
    async def status(self, ctx):
        if ctx.guild.id in premium_guilds:
            serverip = selectquery(sql, 'guilds', 'mcserver', f'guild_id = {ctx.guild.id}')
            if serverip is None:
                await ctx.send(embed=addEmbed(ctx, "red", "This server does not have a minecraft server set", None))
                return
            servername = ctx.guild.name
        else:
            serverip = "play.ham5teak.xyz:25565"
            servername = "Ham5teak"
        server = JavaServer.lookup(serverip)
        status = server.status()
        if serverip == "play.ham5teak.xyz:25565":
            playercount = status.players.online - 20
        else:
            playercount = status.players.online
        if status.latency >= 0.0001:
            server = "Online ✅"
        else:
            server = "Offline ❌"
        embedDescription =(f"**{serverip.split('.', 2)[1].title()} Status:** {server} \n**Players:** {playercount}\n**IP:** {serverip}")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription ))
        return

    @cog_ext.cog_slash(name="move", description="Move a channel to specified category.", )
    async def move(self, ctx, category):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        alias = category
        aliaslist = selectqueryall(sql, "categories", "category_name", f"guild_id = {ctx.guild.id}")
        for stralias in aliaslist:
            if alias == stralias[0]:
                ctxchannel = ctx.channel
                result = selectquery(sql, "categories", "category_id", f"category_name = '{alias}' AND guild_id = {ctx.guild.id}")
                cat = client.get_channel(result)
                await ctxchannel.edit(category=cat)
                embedDescription  = (f"{ctxchannel.mention} has been moved to category {alias}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
                
    @cog_ext.cog_slash(name="join_alpha", guild_ids=[380308776114454528, 1043427380821237770])
    async def join_alpha(self, ctx, build_image):
        await ctx.defer(hidden=True)
        chan = ctx.guild.get_channel(1049404092507750510)
        embedDescription = f"{ctx.author.mention} has joined the competition with user id: {ctx.author.id}"
        if ctx.data["resolved"]["attachments"]:
            async with aiohttp.ClientSession() as session:
                url = ctx.data["resolved"]["attachments"][build_image]["url"]
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(ctx.data["resolved"]["attachments"][build_image]["filename"], mode='wb')
                        await f.write(await resp.read())
                        await f.close()
            emimage = ctx.data["resolved"]["attachments"][build_image]["filename"]
            attach = f"attachment://{emimage}"
            if emimage is not None:
                await chan.send(embed=addEmbed(ctx, "invis", embedDescription, attach, False), file=discord.File(emimage))
                await ctx.send(embed=addEmbed(ctx, "invis", "Successfully applied to competition", attach, False))
                os.remove(f"./{emimage}")
        else:
            await ctx.send(addEmbed(ctx, "red", "Please upload an image of your build", None, False))

    @cog_ext.cog_slash(name="tag", description="A command used to leave a note to a channel")
    async def tag(self, ctx, note, user:discord.User = None, channel:discord.TextChannel = None, role:discord.Role = None):
        moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
        if moderatorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        await ctx.defer(hidden=False)
        finalmentions = []
        mentions = [user, channel, role]
        for mention in mentions:
            if mention is not None:
                if finalmentions == 0:
                    finalmentions.insert(mention.mention)
                finalmentions.append(mention.mention)
        for mention in mentions:
            if mention is not None:
                embedDescription =(f"{ctx.author.mention} has tagged the channel as `{note.upper()}` \n\n**Mentions:** {', '.join(finalmentions)}")
                await ctx.send(embed=addEmbed(ctx,None,embedDescription ))
                return
        embedDescription  = (f"{ctx.author.mention} has tagged the channel as `{note.upper()}`")
        await ctx.send(embed=addEmbed(ctx,None,embedDescription )) 

    # ------- SETTING SLASH COMMANDS -------

    @cog_ext.cog_slash(name="setchannel", description="Set channels for your server")
    @commands.has_permissions(manage_guild=True)
    async def setchannel(self, ctx, value: discord.TextChannel, channel: str):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        guild_id = ctx.guild.id
        channelid = str(value.id)
        commandsloop = ["statuschannel", "alertschannel", "lpalertschannel", "crashalertschannel", "generalchannel"
        , "acceptedsuggestions", "rejectedsuggestions", "demandedsuggestions"]
        for commanda in commandsloop:
            if commanda == channel:
                column = (channel)
                values = (channelid)
                where = (f"guild_id = {guild_id}")
                result = (insertquery(sql, 'guilds', column , values, where))
                if result is not None:
                    embedDescription  = (f"{channel} successfully registered as <#{channelid}>")
                    await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), hidden=True)
                else:
                    embedDescription  = (f"{channel} couldn't be registered as {channelid}")
                    await ctx.send(embed=addEmbed(ctx,"red",embedDescription), hidden=True)
                return
        commandsloop2 = ["announcement", "poll", "suggestion"]
        for commanda in commandsloop2:
            if commanda == channel:
                try:
                    list11 = selectqueryall(sql, 'announcements', 'channel_id', f'guild_id = {ctx.guild.id}')
                    for item in list11:
                        if item[0] == value.id:
                            embedDescription  = (f"{channelid} is already registered.")
                            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))
                            return
                except:
                    pass
                column = '(guild_id  , channel_id , channel_type)'
                values = (guild_id , channelid , channel)
                result = (insertquery(sql, 'announcements', column , values, None))
                if ctx.guild.id not in announcementschannels.keys() or ctx.guild.id not in suggestionchannels.keys() or ctx.guild.id not in pollchannels.keys():
                       announcementschannels[ctx.guild.id] = []
                if channel == "announcement":
                    announcementschannels[ctx.guild.id].append(value.id)
                    channel1 = "an announcement"
                elif channel == "suggestion":
                    suggestionchannels[ctx.guild.id].append(value.id)
                    channel1 = "a suggestion"
                elif channel == "poll":
                    pollchannels[ctx.guild.id].append(value.id)
                    channel1 = "a poll"
                if (result == 0):
                    embedDescription  = (f"Successfully registered <#{channelid}> as {channel1} channel.")
                    await ctx.send(embed=addEmbed(ctx,"green",embedDescription ))
                else:
                    embedDescription  = (f"Couldn't register <#{channelid}> as {channel1} channel.")
                    await ctx.send(embed=addEmbed(ctx,"red",embedDescription ))
                return

            
    @cog_ext.cog_slash(name="setmove")
    @commands.has_permissions(manage_guild=True)
    async def setmove(self, ctx, categoryi: discord.CategoryChannel, alias):
        await administratorcheck(ctx.guild, ctx.author)
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        movecheck = selectquery(sql, 'guilds', 'custommovecount', f'guild_id = {ctx.guild.id}')
        if movecheck >= 45:
            await ctx.send(embed=addEmbed(ctx, None, f"Guild has {movecheck} custommoves set which is over the limit."), hidden=True)
            return
        guild_id = ctx.guild.id
        categoryid = str(categoryi.id)
        categoryname = str(alias).replace('"', '').replace("'", "")
        categoryn = selectqueryall(sql, 'categories', 'category_name', f'guild_id = {ctx.guild.id}')
        for stralias in categoryn:
            if categoryname == stralias[0]:
                embedDescription  =(f"Category `{categoryname}` already exists.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), hidden=True)
                return 1
        column = '(guild_id, category_name)'
        values = (guild_id, categoryname)
        where = None
        result = (insertquery(sql, 'categories', column , values, where))
        column = ('category_id')
        values = (categoryid)
        where = (f"category_name = '{categoryname}'")
        result = (insertquery(sql, 'categories', column , values, where))
        if (result == 0):
            embedDescription =(f"Successfully registered {categoryname} as `{categoryid}`")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)   
            insertquery(sql, 'guilds', 'custommovecount', f'{len(categoryn) + 1}', f'guild_id = {ctx.guild.id}')
        else:
            embedDescription  =(f"Couldn't register {categoryname} as `{categoryid}`")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), hidden=True)

    @cog_ext.cog_slash(name="setrole")
    @commands.has_permissions(manage_guild=True)
    async def setrole(self, ctx, administrator:discord.Role, moderator: discord.Role):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        result = selectquery(sql, 'guilds', 'moderator_id', f'guild_id = {ctx.guild.id}')
        if result is None:
            embedDescription  = (f"Server needs to be setup before executing this command.")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
        elif result is not None:
            a = insertquery(sql, "guilds", "moderator_id", f"{moderator.id}", f"guild_id = {ctx.guild.id}")
            b = insertquery(sql, "guilds", "administrator_id", f"{administrator.id}", f"guild_id = {ctx.guild.id}")
            if (a == 0) and (b == 0):
                embedDescription  = (f"New administrator and moderator roles have successfully been set as {administrator.mention} {moderator.mention}")
                await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), hidden=True)
            else:
                embedDescription  = (f"Couldn't register {administrator.mention} {moderator.mention} as administrator and moderator.")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), hidden=True)

    @cog_ext.cog_slash(name="setserver")
    async def setserver(self, ctx, serverip: str):
        administratorcheck1 = await administratorcheck(ctx.guild, ctx.author)
        if administratorcheck1 == 0:
            await ctx.send(embed=await nopermission(ctx), hidden=True)
            return
        try:
            server = JavaServer.lookup(serverip)
            status = server.status()
        except:
            embedDescription  = (f"Couldn't register {serverip} as server ip.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), hidden=True)
            return
        guild_id = str(ctx.guild.id)
        where = (f"guild_id = {guild_id}")
        result = (insertquery(sql, 'guilds', 'mcserver', f"'{serverip}'", where))
        if (result == 0):
            embedDescription  = (f"Successfully registered {serverip} as server ip.")
            await ctx.send(embed=addEmbed(ctx,"green",embedDescription ), hidden=True)
        else:
            embedDescription  = (f"Couldn't register {serverip} as server ip.")
            await ctx.send(embed=addEmbed(ctx,"red",embedDescription ), hidden=True)

    @cog_ext.cog_slash(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx, password, administrator:discord.Role, moderator:discord.Role):
        async def invalidpass():
            embedDescription  = (f"Invalid password.")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), hidden=True)
        cc = password[:16]
        password = password[16:].strip()
        if verify(cc) == False:
            await invalidpass()
            return
        elif verify(cc) == True:
            check = selectqueryall(sql, f'passwords', 'password', None)
            for pass1 in check:
                if pass1[0] != password:
                    found = False
                if pass1[0] == password:
                    found = True
            if found != True:
                await invalidpass()
                return
            check2 = selectquery(sql, f'passwords', 'used', f"password = '{password}'")
            if check2 == 1:
                embedDescription  = (f"This password was already used.")
                await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), hidden=True)
                return
            elif check2 == 0:
                insertquery(sql, f'passwords', 'used', '(1)', f'password = "{str(password)}"')
                insertquery(sql, f'passwords', 'guild_id', f'{ctx.guild.id}', f'password = "{str(password)}"')
        guild_id = ctx.guild.id
        if guild_id in premium_guilds:
            embedDescription  = (f"You are already logged in as Premium.")
            await ctx.send(embed=addEmbed(ctx,"dark_teal",embedDescription), hidden=True)
            return
        else:
            guild_name = ctx.guild.name
            column = '(guild_id , guild_name , premium , administrator_id , moderator_id)'
            values = (guild_id , guild_name , True , administrator.id , moderator.id)
            where = None
            insertquery(sql, 'guilds' , column , values, where)
            insertcheck = selectquery(sql, 'guilds', 'premium', f'guild_id = {ctx.guild.id}')   
            premium_guilds.append(ctx.guild.id) 
            if insertcheck != 0:
                embedDescription  = (f"Setup successfully completed!")
                await ctx.send(embed=addEmbed(ctx,"green",embedDescription), hidden=True)
            else:
                embedDescription  = (f"Setup failed!")
                await ctx.send(embed=addEmbed(ctx,"red",embedDescription), hidden=True)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        print(error)
        if isinstance(error, discord.errors.NotFound):
            try:
                embedDescription  = (f"Please enter a valid ID. \n{error}")
                await ctx.send(embed=addEmbed(ctx,"teal",embedDescription ), hidden=True)
            except:
                return
        if isinstance(error, commands.MissingPermissions):
            embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
        if isinstance(error, commands.ChannelNotFound):
            embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
        if isinstance(error, commands.RoleNotFound):
            embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
        if isinstance(error, commands.MemberNotFound):
            embedDescription  = (f"Please make sure you have entered all values correctly.\n{error}")
            await ctx.send(embed=addEmbed(ctx,None,embedDescription ), hidden=True)
        else:
            await ctx.send(embed=addEmbed(None, "red", f"Unknown error: {error}", None), hidden=True)

def setup(client):
    client.add_cog(Slash(client))