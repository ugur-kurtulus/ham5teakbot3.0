import discord
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select_option, create_select, wait_for_component
from discord_slash.model import ButtonStyle
from discord.ext.commands import command, Cog
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
            nitrorole = ctx.guild.get_role(
                585709169521459212)  # Nitro booster role
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
        embed = addEmbed(None, "invis", f"{ctx.author.mention} has invited you to a tic-tac-toe game.")
        acceptdenycomps = create_actionrow(
            create_button(style=ButtonStyle.green, label="Accept"),
            create_button(style=ButtonStyle.red, label="Decline"))
        board = [
            create_actionrow(create_button(style=ButtonStyle.grey, label="⠀", custom_id="0 0"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="0 1"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="0 2")
             ),
            create_actionrow(create_button(style=ButtonStyle.grey, label="⠀", custom_id="1 0"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="1 1"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="1 2")
             ),
            create_actionrow(create_button(style=ButtonStyle.grey, label="⠀", custom_id="2 0"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="2 1"),
             create_button(style=ButtonStyle.grey, label="⠀", custom_id="2 2")
            )]
        selections = [
            ["unchosen",
             "unchosen",
             "unchosen"],
            ["unchosen",
             "unchosen",
             "unchosen"],
            ["unchosen",
             "unchosen",
             "unchosen"]]
        m = await ctx.send(embed=embed, components=[acceptdenycomps])

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
        else:
            accept = False
            await m.edit(embed=addEmbed(None, "invis", f"{member.mention} has declined the game."), components=[])
            return

        async def winner(team, board):
            if team == "red":
                user = member
            if team == "green":
                user = ctx.author
            try:
                for row in board:
                    for button in row['components']:
                        button['disabled'] = True
            except:
                pass
            await m.edit(embed=addEmbed(None, "invis", f"{user.mention} has won the game!"), components=board)
            return

        greensturnembed = discord.Embed(color=0x2f3037, description=f"{ctx.author.mention}'s turn")
        redsturnembed = discord.Embed(color=0x2f3037, description=f"{member.mention}'s turn")
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
                    listid = res.custom_id
                    firstpart, secondpart = listid.split(' ')
                    for row in board:
                        for button in row['components']:
                            if button["custom_id"] == res.custom_id:
                                button['disabled'] = True
                                button['label'] = "X"
                                button['style'] = ButtonStyle.green
                    selections[int(firstpart)][int(secondpart)] = "green"
                    if haswon('green'):
                        await winner('green', board)
                        accept = False
                        return
                    if istie('green'):
                        await m.edit(embed=addEmbed(None, "invis", "It is a tie!"), components=board)
                        accept = False
                        return
                    greenstatus = False
                    pass
                except asyncio.TimeoutError:
                    for row in board:
                        for button in row['components']:
                            button['disabled'] = True
                    await m.edit(
                        embed=addEmbed(None, "invis", "Timedout!"),components=board)
                    return
                except Exception as exception:
                    print(exception)
            if not greenstatus:
                await m.edit(embed=redsturnembed, components=board)
                try:
                    res = await wait_for_component(client, messages=m, check=redsturncheck, timeout=30)
                    await res.defer(edit_origin=True)
                    listid = res.custom_id
                    firstpart, secondpart = listid.split(' ')
                    for row in board:
                        for button in row['components']:
                            if button["custom_id"] == res.custom_id:
                                button['disabled'] = True
                                button['label'] = "O"
                                button['style'] = ButtonStyle.red
                    selections[int(firstpart)][int(secondpart)] = "red"
                    if haswon('red'):
                        await winner('red', board)
                        accept = False
                        return
                    if istie('red'):
                        await m.edit(embed=addEmbed(None, "invis", "It is a tie!"))
                        accept = False
                        return
                    greenstatus = True
                    pass
                except asyncio.TimeoutError:
                    for row in board:
                        for button in row['components']:
                            button['disabled'] = True
                    await m.edit(
                        embed=addEmbed(None, "invis", "This game has timedout."),
                        components=board)
                    return
                except Exception as exception:
                    print(exception)

    @tictactoe.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await deletemessage(ctx)
            await ctx.send(embed=addEmbed(None, "red", f'Please state the user you would like to play with. `{getprefix2(ctx)}tictactoe <user>`'), delete_after=5)
        else:
            await unknownerror(ctx, error)


def setup(client):
    client.add_cog(TicTacToe(client))