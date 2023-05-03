import datetime
import discord
from typing import Coroutine, Union
import pytz
from discord.ext import commands
from birthdaydb import BirthdayDB
from typing import List

def today_birthday(date) -> bool:
	today: datetime.date = datetime.date.today()
	return today.month == date.month and today.day == date.day

def tmr_birthday(date: datetime.date) -> bool:
	tmr: datetime.date = datetime.date.today() + datetime.timedelta(days=1)
	return tmr.month == date.month and tmr.day == date.day

async def create_thread(message: discord.Message, birthday_star_name: str) -> Coroutine[None, any, None]:
	old_thread: discord.Thread = discord.utils.get(message.channel.threads, name=f"{birthday_star_name}'s Birthday thread")
	if old_thread:
		return

	await message.create_thread(name=f"{birthday_star_name}'s Birthday thread")
	await message.channel.send(f"Created a thread for our birthday star {birthday_star_name}!")

async def delete_expired_threads(birthdays: List[tuple], channels: List[discord.TextChannel]) -> Coroutine[None, any, None]:
	threshold_time: datetime.date = (datetime.datetime.now() - datetime.timedelta(hours=48)).replace(tzinfo=pytz.timezone('UTC'))
	for channel in channels:
		threads: List[discord.Thread] = channel.threads
		for thread in threads:
			if thread.created_at < threshold_time:
				await thread.delete()
				await channel.send(f"Deleted thread {thread.name}.")


def channels_only(channel_ids: List[int]):
	def wrapper(ctx: commands.context.Context):
		return ctx.channel.id in channel_ids
	
	return commands.check(wrapper)

async def create_birthday_channel(guild: discord.Guild) -> discord.TextChannel:
	channel_name = 'Birthday Celebration'
	birthday_channel: discord.TextChannel = discord.utils.get(guild.channels, name=channel_name)
	if not birthday_channel:
		birthday_channel = await guild.create_text_channel(channel_name)
		await birthday_channel.send("Birthday Celebration Channel has been created!")
	return birthday_channel

async def service_in_new_server(guild: discord.Guild, db: BirthdayDB, bot: commands.Bot):
	birthday_channel = await create_birthday_channel(guild)
	db.create_new_server(guild.id, birthday_channel.id)
	await bot.process_commands(commands.Command(name='help').set_author(bot.user))
	await birthday_channel.send(f'Thank you for adding me to your server, {guild.name}! To get started, try using the `!help` command.')



# Init last check to yesterday
last_birthday_check: datetime.date = datetime.date.today() - datetime.timedelta(days=1)
