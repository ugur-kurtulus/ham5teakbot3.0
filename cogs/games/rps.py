import discord
from discord.ext.commands import command, Cog
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
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
        embed=addEmbed(ctx, "invis", f"{ctx.author} has invited you to a rock paper scissors game.")
        acceptdenycomps = [
            [Button(style=ButtonStyle.green, label="Accept"),
            Button(style=ButtonStyle.red, label="Decline")]]
        board = [
            [Button(style=ButtonStyle.grey, label="Rock", id="rock", emoji=client.get_emoji(853978484263223297)),
            Button(style=ButtonStyle.grey, label="Paper", id="paper", emoji="📄"),
            Button(style=ButtonStyle.grey, label="Scissors", id="scissors", emoji="✂️")
            ]]
        selections = {}
        m = await ctx.send(embed=embed, components=acceptdenycomps, content=member.mention)
        def haswon(author, user):
            if selections[author.id] == "rock" and selections[user.id] == "paper":
                return user
            elif selections[author.id] == "rock" and selections[user.id] == "scissors":
                return author
            elif selections[author.id] == "paper" and selections[user.id] == "rock":
                return author
            elif selections[author.id] == "paper" and selections[user.id] == "scissors":
                return user
            elif selections[author.id] == "scissors" and selections[user.id] == "paper":
                return author
            elif selections[author.id] == "scissors" and selections[user.id] == "rock":
                return user
        def istie(author, user):
            if selections[author.id] == selections[user.id]:
                return True
            else:
                return False


        def confirmcheck(res):
            return res.user.id == member.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id)

        try:
            res = await self.bot.wait_for("button_click", check=confirmcheck, timeout=50)
        except asyncio.TimeoutError:
            await m.edit(
                embed=addEmbed(ctx, "invis", "This game has timedout."),
                components=[Button(style=ButtonStyle.red, label="This game has timedout!", disabled=True)])
            return
        await res.respond(type=6)
        if res.component.label == "Accept":
            accept = True
            await m.edit(embed=addEmbed(ctx, "invis", f"{member} has accepted the game."), components=[])
            await asyncio.sleep(1)

        else:
            accept = False
            await m.edit(embed=addEmbed(ctx, "invis", f"{member} has declined the game."), components=[])
            return
        
        async def winner(team, board):
            if team == "red":
                user = member
            if team == "green":
                user = ctx.author
            await m.edit(embed=addEmbed(ctx, "invis", f"{user} has won the game!"), components=board)
            return
        
        greensturnembed = discord.Embed(color=0x2f3037, description=f"{ctx.author}'s turn")
        redsturnembed = discord.Embed(color=0x2f3037, description=f"{member}'s turn")
        redsturnembed.set_author(name=member, icon_url=member.avatar_url)
        greensturnembed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        greenstatus = True
        def greensturncheck(res):
            return res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and res.message.id == m.id
        def redsturncheck(res):
            return res.user.id == member.id and res.channel.id == ctx.channel.id and res.message.id == m.id
        while accept:
            if greenstatus:
                await m.edit(embed=greensturnembed, components=board)
                try:
                    res = await self.bot.wait_for("button_click", check=greensturncheck, timeout=15)
                    await res.respond(type=6)
                    selections.update({res.user.id: res.component.id})
                    greenstatus = False
                    pass

                except asyncio.TimeoutError:
                    await m.edit(
                        embed=addEmbed(ctx, "invis", "Timedout!"),
                        components=[Button(style=ButtonStyle.red, label="This game has timedout!", disabled=True)])
                    return
            if not greenstatus:
                await m.edit(embed=redsturnembed, components=board)
                try:
                    res = await self.bot.wait_for("button_click", check=redsturncheck, timeout=15)
                    await res.respond(type=6)
                    selections.update({res.user.id: res.component.id})
                    board = [Button(style=ButtonStyle.blue, label=f"{res.user}'s choice: {res.component.id}", disabled=True), Button(style=ButtonStyle.blue, label=f"{ctx.author}'s choice: {selections[ctx.author.id]}", disabled=True)]
                    if istie(ctx.author, res.user):
                        await m.edit(embed=addEmbed(None, "invis", "It is a tie!"), components=[board])
                        accept = False
                        return
                    else:
                        winner = haswon(ctx.author, res.user)
                        await m.edit(embed=addEmbed(None, "invis", f"{winner} won the match!"), components=[board])
                        accept = False
                        return

                except asyncio.TimeoutError:
                    await m.edit(
                        embed=addEmbed(ctx, "invis", "This game has timedout."),
                        components=[Button(style=ButtonStyle.red, label="This game has timedout!", disabled=True)])
                    return

    @rps.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please state the user you would like to play with. `{getprefix2(ctx)}rps <user>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

def setup(client):
    DiscordComponents(client)
    client.add_cog(RPS(client))