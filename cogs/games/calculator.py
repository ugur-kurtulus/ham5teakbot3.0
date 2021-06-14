import ast
import datetime
from typing import Type
import discord
import math
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from discord_slash import cog_ext
from utils.functions import *

buttons = [
    [Button(style=ButtonStyle.grey, label="1"),
    Button(style=ButtonStyle.grey, label="2"),
    Button(style=ButtonStyle.grey, label="3"),
    Button(style=ButtonStyle.blue, label="×"),
    Button(style=ButtonStyle.red, label="Exit")],
    [Button(style=ButtonStyle.grey, label="4"),
    Button(style=ButtonStyle.grey, label="5"),
    Button(style=ButtonStyle.grey, label="6"),
    Button(style=ButtonStyle.blue, label="÷"),
    Button(style=ButtonStyle.red, label="←")],
    [Button(style=ButtonStyle.grey, label="7"),
    Button(style=ButtonStyle.grey, label="8"),
    Button(style=ButtonStyle.grey, label="9"),
    Button(style=ButtonStyle.blue, label="+"),
    Button(style=ButtonStyle.red, label="Clear")],
    [Button(style=ButtonStyle.grey, label="00"),
    Button(style=ButtonStyle.grey, label="0"),
    Button(style=ButtonStyle.grey, label="."),
    Button(style=ButtonStyle.blue, label="-"),
    Button(style=ButtonStyle.green, label="=")],
    [Button(style=ButtonStyle.grey, label="("),
    Button(style=ButtonStyle.grey, label=")"),
    Button(style=ButtonStyle.grey, label="π"),
    Button(style=ButtonStyle.grey, label="x²"),
    Button(style=ButtonStyle.grey, label="x³")]]


def calculate(exp):
    o = exp.replace("×", "*")
    o = o.replace("÷", "/")
    o = o.replace("π", str(math.pi))
    o = o.replace("²", "**2")
    o = o.replace("³", "**3")
    result = ""
    try:
        result = str(eval(o)) #nosec
    except BaseException:
        result = "An error occurred."

    return result

class Calculator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dc = DiscordComponents(self.client)

    @commands.command(aliases=['calc', 'c'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def calculator(self, ctx):
        if ctx.guild.id == 380308776114454528:
            if "staff" not in ctx.channel.name and "bot" not in ctx.channel.name and "games" not in ctx.channel.name and "calc" not in ctx.channel.name:
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
        m = await ctx.send(content="Loading Calculators...")
        expression = " "
        delta = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        e = discord.Embed(title=f"{ctx.author}'s calculator", description=f"```\n{expression}\n```", timestamp=delta,color=colors["invis"])
        await m.edit(content=" ", components=buttons, embed=e)
        while m.created_at < delta: 
            try:
                res = await self.client.wait_for("button_click", timeout=120)
                if (res.author.id == ctx.author.id and res.message.embeds[0].timestamp < delta):
                    expression = res.message.embeds[0].description[6:-3]
                    if expression == " " or expression == "An error occurred.":
                        expression = ""
                    if res.component.label == "Exit":
                        e = discord.Embed(title=f"{ctx.author}'s calculator", description="```\nClosed Calculator\n```" ,color=colors["invis"])
                        await res.respond(embed=e, type=7, components=[Button(label="This calculator has been closed.", style=ButtonStyle.red, disabled=True)])
                        break
                    elif res.component.label == "←":
                        expression = expression[:-1]
                    elif res.component.label == "Clear":
                        expression = " "
                    elif res.component.label == "=":
                        expression = calculate(expression)
                    elif res.component.label == "x²":
                        expression += "²"
                    elif res.component.label == "x³":
                        expression += "³"
                    else:
                        expression += res.component.label
                    f = discord.Embed(title=f"{ctx.author}'s calculator",description=f"```xl\n{expression}```",timestamp=delta,color=colors["invis"])
                    await res.respond(content="", embed=f, components=buttons, type=7)
            except asyncio.TimeoutError:
                await m.edit(embed=discord.Embed(title=f"{ctx.author}'s calculator", description="```\nTimedout Calculator\n```" ,color=colors["invis"]), 
                components=[Button(label="This calculator has timed out.", style=ButtonStyle.red, disabled=True)])

    @calculator.error
    async def clear_error(self, ctx, error):
        if isinstance(error, TypeError):
            print(error)
        await unknownerror(ctx, error)
        
def setup(client):
    client.add_cog(Calculator(client))