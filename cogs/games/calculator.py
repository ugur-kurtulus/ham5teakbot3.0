import ast
from venv import create
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select_option, create_select, wait_for_component
from discord_slash.model import ButtonStyle
import datetime
from typing import Type
import discord
import math
from discord.ext import commands
from discord_slash import cog_ext
from utils.functions import *

buttons = [
    create_actionrow(create_button(style=ButtonStyle.grey, label="1"),
    create_button(style=ButtonStyle.grey, label="2"),
    create_button(style=ButtonStyle.grey, label="3"),
    create_button(style=ButtonStyle.blue, label="×"),
    create_button(style=ButtonStyle.red, label="Exit")),
    create_actionrow(create_button(style=ButtonStyle.grey, label="4"),
    create_button(style=ButtonStyle.grey, label="5"),
    create_button(style=ButtonStyle.grey, label="6"),
    create_button(style=ButtonStyle.blue, label="÷"),
    create_button(style=ButtonStyle.red, label="←")),
    create_actionrow(create_button(style=ButtonStyle.grey, label="7"),
    create_button(style=ButtonStyle.grey, label="8"),
    create_button(style=ButtonStyle.grey, label="9"),
    create_button(style=ButtonStyle.blue, label="+"),
    create_button(style=ButtonStyle.red, label="Clear")),
    create_actionrow(create_button(style=ButtonStyle.grey, label="00"),
    create_button(style=ButtonStyle.grey, label="0"),
    create_button(style=ButtonStyle.grey, label="."),
    create_button(style=ButtonStyle.blue, label="-"),
    create_button(style=ButtonStyle.green, label="=")),
    create_actionrow(create_button(style=ButtonStyle.grey, label="("),
    create_button(style=ButtonStyle.grey, label=")"),
    create_button(style=ButtonStyle.grey, label="π"),
    create_button(style=ButtonStyle.grey, label="x²"),
    create_button(style=ButtonStyle.grey, label="x³"))]


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

    @commands.command(aliases=['calc', 'c'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def calculator(self, ctx):
        if ctx.guild.id == 380308776114454528:
            if "staff" not in ctx.channel.name and "bot" not in ctx.channel.name and "games" not in ctx.channel.name and "calc" not in ctx.channel.name:
                return
        m = await ctx.send(content="Loading Calculators...")
        expression = " "
        delta = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        e = discord.Embed(title=f"{ctx.author}'s calculator", description=f"```\n{expression}\n```", timestamp=delta,color=colors["invis"])
        await m.edit(content=" ", components=buttons, embed=e)
        while m.created_at < delta: 
            try:
                res = await wait_for_component(client, messages=m, timeout=120)
                await res.defer(edit_origin=True)
                if (res.author.id == ctx.author.id and res.origin_message.embeds[0].timestamp < delta):
                    expression = res.origin_message.embeds[0].description[6:-3]
                    if expression == " " or expression == "An error occurred.":
                        expression = ""
                    if res.component.get('label') == "Exit":
                        e = discord.Embed(title=f"{ctx.author}'s calculator", description="```\nClosed Calculator\n```" ,color=colors["invis"])
                        await m.edit(embed=e, components=[create_actionrow(create_button(label="This calculator has been closed.", style=ButtonStyle.red, disabled=True))])
                        break
                    elif res.component.get('label') == "←":
                        expression = expression[:-1]
                    elif res.component.get('label') == "Clear":
                        expression = " "
                    elif res.component.get('label') == "=":
                        expression = calculate(expression)
                    elif res.component.get('label') == "x²":
                        expression += "²"
                    elif res.component.get('label') == "x³":
                        expression += "³"
                    else:
                        expression += res.component.get('label')
                    f = discord.Embed(title=f"{ctx.author}'s calculator",description=f"```xl\n{expression}```",timestamp=delta,color=colors["invis"])
                    await m.edit(content="", embed=f, components=buttons)
            except asyncio.TimeoutError:
                await m.edit(embed=discord.Embed(title=f"{ctx.author}'s calculator", description="```\nTimedout Calculator\n```" ,color=colors["invis"]), 
                components=[create_actionrow(create_button(label="This calculator has been closed.", style=ButtonStyle.red, disabled=True))])

    @calculator.error
    async def clear_error(self, ctx, error):
        if isinstance(error, TypeError):
            print(error)
        await unknownerror(ctx, error)
        
def setup(client):
    client.add_cog(Calculator(client))