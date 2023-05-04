import dotenv
import os
import certifi

# Validate ssl certificate
os.environ["SSL_CERT_FILE"] = certifi.where()

# Load environment variables in the .env file
dotenv.load_dotenv()

from bot import bot
from bot_functions.commands import *
from bot_functions.events import *
from bot_functions.background_tasks import *

bot.run(os.getenv('TOKEN'))
