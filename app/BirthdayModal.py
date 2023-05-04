import discord
from discord.ui import Modal, TextInput
from discord.interactions import Interaction
import datetime
from typing import Coroutine
from birthdaydb import db
from helpers import check_birthday

class BirthdayModal(Modal, title="Birthday Reminder"):
	'''
		A Modal (form) for users to enter their birthday
		Format: mm/dd/yyyy
	'''
	
	username = TextInput(
		label="Your name (real name or nickname)",
		style=discord.TextStyle.short,
		placeholder="John Doe",
		max_length=20,
		min_length=2,
		required=True
	)

	answer = TextInput(
		label="Birthday (dd/mm/yyyy 0000 for anonymous year)",
		style=discord.TextStyle.short,
		placeholder="21/11/2003",
		required=True,
		max_length=10,
		min_length=10
	)

	async def on_submit(self, interaction: Interaction) -> Coroutine:
		if db.birthday_exists(interaction.user, interaction.guild.id):
			await interaction.response.send_message(f"{interaction.user.mention} You have already set your birthday!", ephemeral=True)
			return

		try:
			if self.answer.value.endswith('0000'): # Anonymous birthyear
				birthday = datetime.datetime.strptime(self.answer.value[:5], '%d/%m').date()
				if birthday.year >= datetime.datetime.now().year:
					await interaction.response.send_message(f"Don't born so late bro.", ephemeral=True)
					return
			else:
				birthday = datetime.datetime.strptime(self.answer.value, '%d/%m/%Y').date()
			username = self.username.value
			# year_anonymous = [True, False][birthday.year == 0]
			embed = discord.Embed(
				title=self.title, description=f"{username}\n**{self.answer.value}**", timestamp=datetime.datetime.now(), color=discord.Colour.blue())
			embed.set_author(name=interaction.user,
							icon_url=interaction.user.avatar)
			db.store_birthday(username, birthday, interaction.user, interaction.guild.id)
			await interaction.response.send_message(embed=embed)
			await check_birthday(birthday, interaction.user.id, interaction.channel, username)
		except ValueError:
			await interaction.response.send_message(f"{interaction.user.mention} Invalid birthday format!", ephemeral=True)