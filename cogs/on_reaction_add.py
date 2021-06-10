from discord.ext import commands 
from cogs.functions import *

class on_reaction_add(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        messageid = reaction.message.id
        rcount = 8
        if "suggestions" in reaction.message.channel.name and "staff-suggestions" not in reaction.message.channel.name:
            if reaction.emoji == "✅":
                if reaction.count == rcount:
                    dsuggestions = selectquery(sql, 'guilds', 'demandedsuggestions', f'guild_id = {reaction.message.guild.id}')
                    channel = reaction.message.channel
                    if dsuggestions is None:
                        return
                    dsuggestionschannel = client.get_channel(dsuggestions)
                    msg = await channel.fetch_message(messageid)
                    suggestioncheck = await client.get_channel(dsuggestions).history(limit=20).flatten()
                    for sc in suggestioncheck:
                        if f'https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}' in sc.content:
                            return
                    try:
                        finalcount = int(reaction.count - 1)
                        embedDescription  = (f"**{finalcount} Upvotes:** [Go To Suggestion]({msg.jump_url}) - {reaction.message.channel.mention}")
                        embed1 = addEmbed(None,"dark_teal",embedDescription)
                        embed2 = msg.embeds[0]
                        await sendwebhook(reaction.message, "Demanded Suggestions", dsuggestionschannel, None, [embed1, embed2])
                    except AttributeError as e:
                        print(f"{reaction.message.guild.name} doesn't have a demanded suggestions channel set.")
                    return
            elif reaction.emoji == "❌":
                if reaction.count == rcount:
                    rsuggestions = selectquery(sql, 'guilds', 'rejectedsuggestions', f'guild_id = {reaction.message.guild.id}')
                    channel = reaction.message.channel
                    if rsuggestions is None:
                        return
                    rsuggestionschannel = client.get_channel(rsuggestions)
                    msg = await channel.fetch_message(messageid)
                    try:
                        suggestioncheck = await client.get_channel(rsuggestions).history(limit=20).flatten()
                        for sc in suggestioncheck:
                            if f'https://discordapp.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{messageid}' in sc.content:
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
    client.add_cog(on_reaction_add(client))