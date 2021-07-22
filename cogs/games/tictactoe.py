import discord
from discord.ext.commands import command, Cog
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
import asyncio
from utils.functions import *


class TicTacToe(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['ttt', 'titato', 't'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def tictactoe(self, ctx, member: discord.Member):
        if ctx.guild.id == 380308776114454528:
            if "staff" not in ctx.channel.name and "bot" not in ctx.channel.name and "games" not in ctx.channel.name and "tic" not in ctx.channel.name:
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
        embed=addEmbed(ctx, "invis", f"{ctx.author} has invited you to a tic-tac-toe game.")
        acceptdenycomps = [
            [Button(style=ButtonStyle.green, label="Accept"),
            Button(style=ButtonStyle.red, label="Decline")]]
        board = [
            [Button(style=ButtonStyle.grey, label="⠀", id="0 0"),
            Button(style=ButtonStyle.grey, label="⠀", id="0 1"),
            Button(style=ButtonStyle.grey, label="⠀", id="0 2")
            ],
            [Button(style=ButtonStyle.grey, label="⠀", id="1 0"),
            Button(style=ButtonStyle.grey, label="⠀", id="1 1"),
            Button(style=ButtonStyle.grey, label="⠀", id="1 2")
            ],
            [Button(style=ButtonStyle.grey, label="⠀", id="2 0"),
            Button(style=ButtonStyle.grey, label="⠀", id="2 1"),
            Button(style=ButtonStyle.grey, label="⠀", id="2 2")
            ]]
        selections = [
            ["unchosen",
            "unchosen",
            "unchosen"
            ],
            ["unchosen",
            "unchosen",
            "unchosen"
            ],
            ["unchosen",
            "unchosen",
            "unchosen"
            ]]
        m = await ctx.send(embed=embed, components=acceptdenycomps, content=member.mention)
        def haswon(team):
            if selections[0][0] == team and selections[0][1] == team and selections[0][2] == team:
                return True
            if selections[1][0] == team and selections[1][1] == team and selections[1][2] == team:
                return True
            if selections[2][0] == team and selections[2][1] == team and selections[2][2] == team:
                return True
            if selections[0][0] == team and selections[1][0] == team and selections[2][0] == team:
                return True
            if selections[0][1] == team and selections[1][1] == team and selections[2][1] == team:
                return True
            if selections[0][2] == team and selections[1][2] == team and selections[2][2] == team:
                return True
            if selections[0][0] == team and selections[1][1] == team and selections[2][2] == team:
                return True
            if selections[0][2] == team and selections[1][1] == team and selections[2][0] == team:
                return True
            else:
                return False
        def istie(team):
            if not "unchosen" in str(selections):
                if not haswon(team):
                    return True
                else:
                    return False
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
                    res = await self.bot.wait_for("button_click", check=greensturncheck, timeout=50)
                    await res.respond(type=6)
                    listid = res.component.id
                    firstpart, secondpart = listid.split(' ')
                    board[int(firstpart)][int(secondpart)] = Button(style=ButtonStyle.green, label="X", id="1 0", disabled=True)
                    selections[int(firstpart)][int(secondpart)] = "green"
                    if haswon('green'):
                        await winner('green', board)
                        accept = False
                        return
                    if istie('green'):
                        await m.edit(embed=addEmbed(ctx, "invis", "It is a tie!"), components=board)
                        accept = False
                        return
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
                    res = await self.bot.wait_for("button_click", check=redsturncheck, timeout=50)
                    await res.respond(type=6)
                    listid = res.component.id
                    firstpart, secondpart = listid.split(' ')
                    board[int(firstpart)][int(secondpart)] = Button(style=ButtonStyle.red, label="O", id="1 0",
                                                                 disabled=True)
                    selections[int(firstpart)][int(secondpart)] = "red"
                    if haswon('red'):
                        await winner('red', board)
                        accept = False
                        return
                    if istie('red'):
                        await m.edit(embed=addEmbed(ctx, "invis", "It is a tie!"))
                        accept = False
                        return
                        
                    greenstatus = True
                    pass
                except asyncio.TimeoutError:
                    await m.edit(
                        embed=addEmbed(ctx, "invis", "This game has timedout."),
                        components=[Button(style=ButtonStyle.red, label="This game has timedout!", disabled=True)])
                    return

    @tictactoe.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed2(ctx, "red", f'Please state the user you would like to play with. `{getprefix2(ctx)}tictactoe <user>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)

def setup(client):
    DiscordComponents(client)
    client.add_cog(TicTacToe(client))