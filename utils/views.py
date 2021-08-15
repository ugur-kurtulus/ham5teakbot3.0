from utils.functions import *
import discord

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = 0

    prevdis = True
    nextdis = False

    @discord.ui.button(label='←', style=discord.ButtonStyle.green, disabled=prevdis)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if len(pages) != 1:
            self.value -= 1
        for item in self.children:
            if item.label == "←":
                if (self.value - 1) < 0:
                    item.disabled = True
        for item in self.children:
            if item.label == "→":
                if len(pages) - 1 != self.value:
                    item.disabled = False
        for item in self.children:
            if item.custom_id == "current":
                item.label = f"{self.value+1}/{len(pages)}"
        await interaction.message.edit(embed=pages[self.value], view=self)

    @discord.ui.button(label=f'1/{len(pages)}', style=discord.ButtonStyle.grey, disabled=True, custom_id="current")
    async def current(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label='→', style=discord.ButtonStyle.green, disabled=nextdis)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if len(pages) != 1:
            self.value += 1
        for item in self.children:
            if item.label == "←":
                if (self.value - 1) >= 0:
                    item.disabled = False
        for item in self.children:
            if item.label == "→":
                if len(pages) - 1 == self.value:
                    item.disabled = True
        for item in self.children:
            if item.custom_id == "current":
                item.label = f"{self.value+1}/{len(pages)}"
        await interaction.message.edit(embed=pages[self.value], view=self)

class OPVerification(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.red, custom_id='persistent_view:verify')
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
            item.label = f"OP Verified By {interaction.user.name}#{interaction.user.discriminator}"
            item.style=discord.ButtonStyle.green
        await interaction.message.edit(view=self)
        await interaction.response.send_message('Op successfully verified.', ephemeral=True)