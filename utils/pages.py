import discord
import __future__
from utils.functions import *

async def page(ctx, number: int):
    if number == 1:
        return await addEmbed2(ctx, None, """**Channels**
        **1""")
