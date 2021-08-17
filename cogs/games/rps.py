import discord
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select_option, create_select, wait_for_component
from discord_slash.model import ButtonStyle
from discord.ext import commands
from discord.ext.commands import command, Cog
import asyncio
from utils.functions import *


class RPS(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['rockpaperscissors', 'r'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def rps(self, ctx, member: discord.Member):
        if ctx.guild.id == 380308776114454528:
            if "staff" not in ctx.channel.name and "bot" not in ctx.channel.name and "games" not in ctx.channel.name and "rock" not in ctx.channel.name:
                return
            check = 0
            nitrorole = ctx.guild.get_role(585709169521459212) # Nitro booster role
            moderatorcheck1 = await moderatorcheck(ctx.guild, ctx.author)
            if moderatorcheck1 != 0:
                check = 1
            if nitrorole in ctx.author.roles:
                check = 1
            if check != 1:
                await ctx.send(embed=await nopermission(ctx), delete_after=5) 
                return
        if ctx.author.bot or member.bot:
            return
        if ctx.author == member:
            return await ctx.send("You can't play against yourself!")
        embed=addEmbed(None, "invis", f"{ctx.author} has invited you to a rock paper scissors game.")
        acceptdenycomps = create_actionrow(
            create_button(style=ButtonStyle.green, label="Accept"),
            create_button(style=ButtonStyle.red, label="Decline"))
        board = [
            create_actionrow(create_button(style=ButtonStyle.grey, label="Rock", emoji="🪨"),
            create_button(style=ButtonStyle.grey, label="Paper", emoji="📄"),
            create_button(style=ButtonStyle.grey, label="Scissors", emoji="✂️")
            )]
        selections = {}
        m = await ctx.send(embed=embed, components=[acceptdenycomps])
        def haswon(author, user):
            if selections[author.id] == "🪨" and selections[user.id] == "📄":
                return user
            elif selections[author.id] == "🪨" and selections[user.id] == "✂️":
                return author
            elif selections[author.id] == "📄" and selections[user.id] == "🪨":
                return author
            elif selections[author.id] == "📄" and selections[user.id] == "✂️":
                return user
            elif selections[author.id] == "✂️" and selections[user.id] == "📄":
                return author
            elif selections[author.id] == "✂️" and selections[user.id] == "🪨":
                return user
        def istie(author, user):
            if selections[author.id] == selections[user.id]:
                return True
            else:
                return False


        def confirmcheck(res):
            return res.author.id == member.id and res.channel.id == ctx.channel.id and str(res.origin_message.id) == str(m.id)
        try:
            res = await wait_for_component(client, messages=m, check=confirmcheck, timeout=300)
        except asyncio.TimeoutError:
            await m.edit(
                embed=addEmbed(None, "invis", "This game has timedout."),
                components=[create_actionrow(create_button(style=ButtonStyle.red, label="This game has timedout!", disabled=True))])
            return
        await res.defer(edit_origin=True)
        if res.component.get('label') == "Accept":
            accept = True
            await m.edit(embed=addEmbed(None, "invis", f"{member} has accepted the game."), components=[])
            await asyncio.sleep(1)

        else:
            accept = False
            await m.edit(embed=addEmbed(None, "invis", f"{member} has declined the game."), components=[])
            return
        
        async def winner(team, board):
            if team == "red":
                user = member
            if team == "green":
                user = ctx.author
            await m.edit(embed=addEmbed(None, "invis", f"{user} has won the game!"), components=board)
            return
        
        greensturnembed = discord.Embed(color=0x2f3037, description=f"{ctx.author}'s turn")
        redsturnembed = discord.Embed(color=0x2f3037, description=f"{member}'s turn")
        redsturnembed.set_author(name=member, icon_url=member.avatar_url)
        greensturnembed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        greenstatus = True
        def greensturncheck(res):
            return res.author.id == ctx.author.id and res.channel.id == ctx.channel.id and res.origin_message.id == m.id
        def redsturncheck(res):
            return res.author.id == member.id and res.channel.id == ctx.channel.id and res.origin_message.id == m.id
        while accept:
            if greenstatus:
                await m.edit(embed=greensturnembed, components=board)
                try:
                    res = await wait_for_component(client, messages=m, check=greensturncheck, timeout=30)
                    await res.defer(edit_origin=True)
                    selections.update({res.author.id: res.component['emoji']['name']})
                    greenstatus = False
                    pass
                except asyncio.TimeoutError:
                    await m.edit(
                        embed=addEmbed(None, "invis", "Timedout!"),
                        components=[create_actionrow(create_button(style=ButtonStyle.red, label="This game has timedout!", disabled=True))])
                    return
            if not greenstatus:
                await m.edit(embed=redsturnembed, components=board)
                try:
                    res = await wait_for_component(client, messages=m, check=redsturncheck, timeout=30)
                    await res.defer(edit_origin=True)
                    selections.update({res.author.id: res.component['emoji']['name']})
                    board = [create_actionrow(create_button(style=ButtonStyle.blue, label=f"{res.author}'s choice: {res.component['emoji']['name']}", disabled=True), create_button(style=ButtonStyle.blue, label=f"{ctx.author}'s choice: {selections[ctx.author.id]}", disabled=True))]
                    if istie(ctx.author, res.author):
                        await m.edit(embed=addEmbed(None, "invis", "It is a tie!"), components=[*board])
                        accept = False
                        return
                    else:
                        winner = haswon(ctx.author, res.author)
                        await m.edit(embed=addEmbed(None, "invis", f"{winner} won the match!"), components=[*board])
                        accept = False
                        return
                except asyncio.TimeoutError:
                    await m.edit(
                        embed=addEmbed(None, "invis", "This game has timedout."),
                        components=[create_actionrow(create_button(style=ButtonStyle.red, label="This game has timedout!", disabled=True))])
                    return
                except:
                    pass
    @rps.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please state the user you would like to play with. `{getprefix2(ctx)}rps <user>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

def setup(client):
    client.add_cog(RPS(client))