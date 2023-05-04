from bot import bot, channel_ids
from helpers import *
from discord.ui import Button, View
from BirthdayModal import BirthdayModal
from discord import Interaction
from birthdaydb import db

@bot.command()
@channels_only(channel_ids)
async def set_birthday(ctx: commands.context.Context):
	"""
		Set your birthday, only once for each user.
	"""
	
	async def send_modal_callback(interaction: Interaction):
		await interaction.response.send_modal(BirthdayModal())
	
	button = Button(label="Click me!", custom_id="my_button", style=discord.ButtonStyle.green)
	button.callback = send_modal_callback
	view = View()
	view.add_item(button)
	await ctx.send(view=view)


@bot.command()
@channels_only(channel_ids)
async def list_birthdays(ctx: commands.context.Context):
	"""
		List all recorded birthdays.
	"""
	birthdays = db.get_sorted_birthdays_in_server(ctx.guild.id)
	if not birthdays:
		await ctx.send("No birthdays set yet.")
		return
	embed = discord.Embed(title="Birthday List", color=0xff69b4)
	for user_id, username, birthday, server_id in birthdays:
		if ctx.guild.id != int(server_id):
			continue
		server = bot.get_guild(int(server_id))
		member = discord.utils.get(server.members, id=int(user_id))
		nickname = member.nick
		if not nickname:
			user = await bot.fetch_user(int(user_id))
			nickname = user.name + '(discord name)'
		strdate = convert_date_to_str(birthday)
		embed.add_field(name=nickname, value=f"{username}'s birthday is on {strdate} \n", inline=False)

	await ctx.send(embed=embed)