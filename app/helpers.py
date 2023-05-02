import datetime
import discord
from typing import Coroutine

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

async def delete_expired_threads(birthdays: list[tuple], channel: discord.TextChannel) -> Coroutine[None, any, None]:
	if not birthdays:
		return

	threshold_time: datetime.date = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
	threads: list[discord.Thread] = channel.threads()
	for thread in threads:
		if thread.created_at < threshold_time:
			await thread.delete()
			await channel.send(f"Deleted thread {thread.name}.")


# Init last check to yesterday
last_birthday_check: datetime.date = datetime.date.today() - datetime.timedelta(days=1)
