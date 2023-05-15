from bot import bot, channel_ids
from helpers import *
from discord.ui import Button, View
from BirthdayModal import BirthdayModal
from discord import Interaction
from birthdaydb import db
import datetime

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

@bot.command()
@channels_only(channel_ids)
async def get_threads(ctx):
	threads = ctx.channel.threads
	for thread in threads:
		name = thread.name
		created_at = thread.created_at.replace(tzinfo=None)
		expire_at = created_at + datetime.timedelta(hours=48)
		try:
			time_left = expire_at - datetime.datetime.utcnow()
			hours, hours_remainder = divmod(time_left.seconds, 3600)
			minutes, seconds = divmod(hours_remainder, 60)
			formatted_time_left = f"{time_left.days} days {hours} hours {minutes} minutes"
			await ctx.send(f"Thread \"{name}\": Created at UTC time {created_at.strftime('%d/%m/%Y %H:%M')}, will expire in {formatted_time_left}")
		except Exception as e:
			await ctx.send(f"Error {e}")
