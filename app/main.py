import discord
from discord.ext import commands, tasks
from discord.interactions import Interaction
from discord.ui import Modal, TextInput, Button, View
from sqlalchemy import create_engine
import datetime
import dotenv
# from pathlib import Path
import os
import asyncio
import certifi
from birthdaydb import BirthdayDB


# Validate ssl certificate
os.environ["SSL_CERT_FILE"] = certifi.where()

# Load environment variables in the .env file
dotenv.load_dotenv()

# Init DB
db = BirthdayDB()


class BirthdayModal(Modal, title="Birthday Reminder"):
    '''
        A Modal (form) for users to enter their birthday
        Format: mm/dd/yyyy
    '''
    answer = TextInput(
        label="Enter your birthday (dd/mm/yyyy) ",
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
            birthday = datetime.datetime.strptime(self.answer.value, '%d/%m/%Y').date()
            embed = discord.Embed(
                title=self.title, description=f"{self.answer.label}\n**{self.answer}**", timestamp=datetime.datetime.now(), color=discord.Colour.blue())
            embed.set_author(name=interaction.user,
                            icon_url=interaction.user.avatar)
            db.store_birthday(birthday, interaction.user)
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
    async def send_modal_callback(interaction: Interaction):
        await interaction.response.send_modal(BirthdayModal())
    
    button = Button(label="Click me!", custom_id="my_button", style=discord.ButtonStyle.green)
    button.callback = send_modal_callback
    view = View()
    view.add_item(button)
    await ctx.send(view=view)

def today_birthday(date):
    today = datetime.date.today()
    if today.month == date.month and today.day == date.day:
        return True
    return False

def tmr_birthday(date):
    tmr = datetime.date.today() + datetime.timedelta(days=1)
    if tmr.month == date.month and tmr.day == date.day:
        return True
    return False

async def check_birthday(): # todo
    birthdays = db.get_birthdays()
    for user_id, birthday in birthdays:
        if today_birthday(birthday):
            channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
            user = await bot.fetch_user(int(user_id))
            await channel.send(f"Happy Birthday! {user.mention}")
        elif tmr_birthday(birthday):
            channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
            user = await bot.fetch_user(int(user_id))
            await channel.send(f"Rememeber tomorrow is your birthday! {user.mention}")


@tasks.loop(seconds=5)
async def background_check_birthday():
    global last_birthday_check

    if last_birthday_check == datetime.date.today() - datetime.timedelta(days=1):  # If last check is yesterday
        last_birthday_check = datetime.date.today() # Change last check to today
        await check_birthday()


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    background_check_birthday.start()


last_birthday_check = datetime.date.today() - datetime.timedelta(days=1)  # Init last check to yesterday

bot.run(os.getenv('TOKEN'))
