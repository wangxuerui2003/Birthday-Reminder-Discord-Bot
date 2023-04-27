# Birthday-Reminder-Discord-Bot
A birthday reminder discord bot written in Python using the discord.py module

<br>

## Environments
1. Create a .env file in the /app directory
2. Add your discord bot token and desired channel id named TOKEN and CHANNEL_ID

<br>

## Setup
<hr>

### Docker (recommended)
```
$ docker-compose up
```
*Simple right? Embrace docker bro*

### Manual (Strongly not recommended)
#### Requirements:
- Python (3.9+)
- MySQL server (8.0 would be the best)

```Bash
$ python3 -m venv venv # Create virtual environment
$ cd app/
$ pip install -r requirements.txt
```
**Then add your MySQL credentials to the .env file:**
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_HOST
- MYSQL_PORT
- MYSQL_DATABASE
```Bash
$ python main.py
```

## Technologies
- Python (discord.py)
- MySQL
- Docker

## How to use
