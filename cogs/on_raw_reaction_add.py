from discord.ext import commands 
from utils.functions import *

class on_raw_reaction_add(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            print(e)
            return
        messageid = message.id
        rcount = 8
        if "suggestions" in channel.name and "staff-suggestions" not in channel.name:
            if str(payload.emoji) == "✅":
                for reaction1 in message.reactions:
                    if str(reaction1.emoji) == str(payload.emoji):
                        reaction = reaction1
                if reaction.count == rcount:
                    dsuggestions = selectquery(sql, 'guilds', 'demandedsuggestions', f'guild_id = {message.guild.id}')
                    if dsuggestions is None:
                        return
                    dsuggestionschannel = client.get_channel(dsuggestions)
                    msg = await channel.fetch_message(messageid)
                    suggestioncheck = await client.get_channel(dsuggestions).history(limit=50).flatten()
                    for sc in suggestioncheck:
                        if message.embeds[0].description == sc.embeds[1].description:
                            return
                    try:
                        finalcount = int(reaction.count - 1)
                        embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {reaction.message.channel.mention}")
                        embed1 = addEmbed(None,"dark_teal",embedDescription)
                        embed2 = msg.embeds[0]
                        await sendwebhook(message, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                    except AttributeError as e:
                        print(f"{message.guild.name} doesn't have a demanded suggestions channel set.")
                    return
            if str(payload.emoji) == "❌":
                for reaction1 in message.reactions:
                    if str(reaction1.emoji) == str(payload.emoji):
                        reaction = reaction1
                if reaction.count == rcount:
                    rsuggestions = selectquery(sql, 'guilds', 'rejectedsuggestions', f'guild_id = {reaction.message.guild.id}')
                    channel = reaction.message.channel
                    if rsuggestions is None:
                        return
                    rsuggestionschannel = client.get_channel(rsuggestions)
                    msg = await channel.fetch_message(messageid)
                    try:
                        suggestioncheck = await client.get_channel(rsuggestions).history(limit=50).flatten()
                        for sc in suggestioncheck:
                            if message.embeds[0].description == sc.embeds[1].description:
                                return
                    except AttributeError as e:
                        print(f"{rsuggestions} channel has no suggestion history.")
                    try:
                        finalcount = int(reaction.count - 1)
                        embedDescription  = (f"**{finalcount} Downvotes:** [Go To Suggestion]({msg.jump_url}) - {reaction.message.channel.mention}")
                        embed1 = addEmbed(None,"dark_teal",embedDescription)
                        embed2 = msg.embeds[0]
                        await sendwebhook(reaction.message, "Rejected Suggestions", rsuggestionschannel, None, [embed1, embed2])
                    except AttributeError as e:
                        print(f"{reaction.message.guild.name} doesn't have a rejected suggestions channel set.")
                    return

def setup(client):
    client.add_cog(on_raw_reaction_add(client))