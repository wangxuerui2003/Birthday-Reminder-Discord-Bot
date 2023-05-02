import discord
from discord.ext import commands, tasks
from discord.interactions import Interaction
from discord.ui import Modal, TextInput, Button, View
from sqlalchemy.exc import InterfaceError
import datetime
import dotenv
import sys
import os
import certifi

from birthdaydb import BirthdayDB
from helpers import *



# Validate ssl certificate
os.environ["SSL_CERT_FILE"] = certifi.where()

# Load environment variables in the .env file
dotenv.load_dotenv()

# Init DB
db = BirthdayDB()
if not db.db_conn_success:
    print("Can't connect to the database!", file=sys.stderr)
    sys.exit()

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

    async def on_submit(self, interaction: Interaction):
        if db.birthday_exists(interaction.user):
            await interaction.response.send_message(f"{interaction.user.mention} You have already set your birthday!", ephemeral=True)
            return

        try:
            if self.answer.value.endswith('0000'):
                birthday = datetime.datetime.strptime(self.answer.value[:5], '%d/%m').date()
            else:
                birthday = datetime.datetime.strptime(self.answer.value, '%d/%m/%Y').date()
            username = self.username.value
            # year_anonymous = [True, False][birthday.year == 0]
            embed = discord.Embed(
                title=self.title, description=f"{self.answer.label}\n**{self.answer}**", timestamp=datetime.datetime.now(), color=discord.Colour.blue())
            embed.set_author(name=interaction.user,
                            icon_url=interaction.user.avatar)
            db.store_birthday(username, birthday, interaction.user)
            await check_birthday()
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message(f"{interaction.user.mention} Invalid birthday format!", ephemeral=True)

# Init Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def set_birthday(ctx):
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
async def list_birthdays(ctx):
    """
        List all recorded birthdays.
    """

    list_of_birthdays = ""
    birthdays = db.get_birthdays()

    if not birthdays:
        return
    
    for user_id, username, birthday in birthdays:
        guild = bot.guilds[0]
        member = await guild.fetch_member(int(user_id))
        list_of_birthdays += f"User \"{member.nick}\": {username}'s birthday is on {str(birthday.day).zfill(2)}/{str(birthday.month).zfill(2)}\n"

    if list_of_birthdays != "":
        await ctx.send(list_of_birthdays)


async def check_birthday():

    birthdays = db.get_birthdays()
    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))

    await delete_expired_threads(birthdays, channel)

    for user_id, username, birthday in birthdays:
        if today_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Happy Birthday {username}! {user.mention}")
            # message.channel.threads[0].name
            await create_thread(message, username)
        elif tmr_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Rememeber tomorrow is your birthday {username}! {user.mention}")
            await create_thread(message, username)


@tasks.loop(hours=12)
async def background_check_birthday():
    global last_birthday_check

    if last_birthday_check == datetime.date.today() - datetime.timedelta(days=1):  # If last check is yesterday
        last_birthday_check = datetime.date.today() # Change last check to today
        await check_birthday()


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    background_check_birthday.start()


bot.run(os.getenv('TOKEN'))
