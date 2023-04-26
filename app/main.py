import discord
from discord.ext import commands
from discord.ui import Select, View
import datetime
import dotenv
from pathlib import Path
import os
import certifi
import asyncio

os.environ["SSL_CERT_FILE"] = certifi.where()

dotenv.load_dotenv(Path('../.env'))

class BirthdayView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Select(custom_id='birthmonth', options=[
            discord.SelectOption(label='January', value='01'),
            discord.SelectOption(label='February', value='02'),
            discord.SelectOption(label='March', value='03'),
            discord.SelectOption(label='April', value='04'),
            discord.SelectOption(label='May', value='05'),
            discord.SelectOption(label='June', value='06'),
            discord.SelectOption(label='July', value='07'),
            discord.SelectOption(label='August', value='08'),
            discord.SelectOption(label='September', value='09'),
            discord.SelectOption(label='October', value='10'),
            discord.SelectOption(label='November', value='11'),
            discord.SelectOption(label='December', value='12')
        ]))
        self.add_item(discord.ui.TextInput(label="birthday", required=True, placeholder="Day", max_length=2))
        self.add_item(discord.ui.TextInput(label="birthyear", required=True, placeholder="Year", max_length=2))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.message.author.id:
            await interaction.response.send_message('You cannot interact with this message.', ephemeral=True)
            return False
        return True

    @property
    def birthday(self):
        month = self.get_item(0).values[0]
        day = self.get_item(1).values[0]
        year = self.get_item(2).values[0]
        return f"{month}/{day}/{year}"
    
class Cog(commands.Cog):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
    
	@commands.command(name="set_birthday")
	async def set_birthday(self, ctx):
		view = BirthdayView()
		message = await ctx.send('Please select your birthday:', view=view)
		# interaction = await self.bot.wait_for('select_option', check=view.interaction_check)
		# await interaction.response.defer()
		# await message.edit(content=f"You selected {view.birthday} as your birthday.")

		# # Check if the birthday is valid
		# try:
		# 	birthday = datetime.datetime.strptime(view.birthday, '%m/%d/%Y')
		# 	await ctx.send('Your birthday is valid!')
		# except ValueError:
		# 	await ctx.send('Please enter a valid date in the format MM/DD/YYYY.')
		await ctx.send("Haha")
    
class Bot(commands.Bot):
	async def on_ready(self):
		print(f'Logged in as {self.user}.')

	async def setup(self):
		await self.add_cog(Cog(self))

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix='!', intents=intents)
asyncio.run(bot.setup())
# tree = discord.app_commands.CommandTree(client)

bot.run(os.getenv('TOKEN'))