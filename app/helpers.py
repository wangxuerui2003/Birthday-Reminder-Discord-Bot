import datetime
import discord
from typing import Coroutine, Union
import pytz
from discord.ext import commands
from birthdaydb import BirthdayDB
from typing import List
from bot import bot
from get_happybirthday_meme import get_random_birthday_meme
from birthdaydb import db

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
	if not channels:
		return
	threshold_time: datetime.date = (datetime.datetime.now() - datetime.timedelta(hours=48)).replace(tzinfo=pytz.timezone('UTC'))
	for channel in channels:
		threads: List[discord.Thread] = channel.threads
		for thread in threads:
			if thread.created_at < threshold_time:
				await thread.delete()
				await channel.send(f"Deleted thread {thread.name}.")


def channels_only(channel_ids: List[str]):
	def wrapper(ctx: commands.context.Context):
		return str(ctx.channel.id) in channel_ids
	
	return commands.check(wrapper)

async def create_birthday_channel(guild: discord.Guild) -> discord.TextChannel:
	channel_name = 'birthday-celebration'
	birthday_channel: discord.TextChannel = discord.utils.get(guild.channels, name=channel_name)
	if not birthday_channel:
		birthday_channel = await guild.create_text_channel(channel_name)
		await birthday_channel.send("The channel birthday-celebration has been created!")
	return birthday_channel


async def service_in_new_server(guild: discord.Guild, db: BirthdayDB):
	birthday_channel = await create_birthday_channel(guild)
	db.add_new_server(guild.id, birthday_channel.id)
	await birthday_channel.send(f'Thank you for adding me to your server, {guild.name}! To get started, try using the `!help` command.')


async def check_birthday(birthdays, channels) -> Coroutine:
    """
        Check all the birthdays for birthday today and tomorrow.
    """

    for user_id, username, birthday, server_id in birthdays:
        channel_id_tuple = db.get_channelid_from_server(server_id)
        if channel_id_tuple:
            channel_id = channel_id_tuple[0]
        channel = discord.utils.get(bot.get_all_channels(), id=int(channel_id))
        if today_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Happy Birthday {username}! {user.mention}")
            meme_url = get_random_birthday_meme()
            if meme_url:
                embed_meme = discord.Embed(title="Happy Birthday!")
                embed_meme.set_image(url=meme_url)
                await channel.send(embed=embed_meme)
            await create_thread(message, username)
        elif tmr_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Rememeber tomorrow is your birthday {username}! {user.mention}")
            await create_thread(message, username)

