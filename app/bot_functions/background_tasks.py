from discord.ext import tasks
from helpers import *
from bot import channel_ids, guild_ids

# Init last check to yesterday
last_birthday_check: datetime.date = datetime.date.today() - datetime.timedelta(days=1)

@tasks.loop(hours=1)
async def background_check_birthday():
    global last_birthday_check

    if last_birthday_check == datetime.date.today() - datetime.timedelta(days=1):  # If last check is yesterday
        last_birthday_check = datetime.date.today() # Change last check to today

        birthdays: List[tuple] = db.get_birthdays()
        channels = [bot.get_channel(int(channel_id)) for channel_id in channel_ids]

        for user_id, username, birthday, server_id in birthdays:
            channel_id_tuple = db.get_channelid_from_server(server_id)
            if channel_id_tuple:
                channel_id = channel_id_tuple[0]
            channel = discord.utils.get(bot.get_all_channels(), id=int(channel_id))
            await check_birthday(birthday, user_id, channel, username)



@tasks.loop(hours=6)
async def background_delete_expired_threads():
    birthdays: List[tuple] = db.get_birthdays()
    channels = [bot.get_channel(int(channel_id)) for channel_id in channel_ids]
    await delete_expired_threads(birthdays, channels)


@tasks.loop(minutes=10)
async def background_check_guilds():
    await check_guilds()