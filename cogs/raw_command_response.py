from multiprocessing.connection import Client
import discord
from discord.ext import commands 
from discord.ext import commands 
from utils.functions import *
from discord.http import Route
from munch import DefaultMunch
from discord.utils import get
import aiohttp
import aiofiles
import os
import datetime

class raw_command_response(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_interaction(self, res):
        try:
            print(res.__dict__)
        except:
            pass
        try:
            print(res.to_dict())
        except:
            pass
        try:
            print(res.type)
        except:
            pass
          
def setup(client):
    client.add_cog(raw_command_response(client))