# Birthday-Reminder-Discord-Bot
A birthday reminder discord bot written in Python using the discord.py module

<br>

## Environments
1. Create a .env file in the /app directory
2. Add your discord bot token and desired channel id named TOKEN and MEMES_API_KEY (see [giphy api](https://developers.giphy.com/)){:target="_blank"}

<br>

## Setup your own
<hr>

### **Docker** (recommended)
```
$ docker-compose up
```
*Simple right? Embrace docker bro*

<br>

### **Manual** (not recommended)
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

<br>

### Invite my bot to your server (Only the server that you are an admin of)
#### Invite url: [Bot invitation](https://discord.com/api/oauth2/authorize?client_id=1099215833374408795&permissions=543313886288&scope=bot){:target="_blank"}

<br>

## Todo (For myself)
- [x] Send random Happy birthday meme while mentioning the birthday boy/girl.
- [x] Create a thread one day before someone's birthday dedicated for him/her, the thread will expire after 48 hours. And if some one just set their birthday on their birthday, create a thread as well.
- [x] List everyone's birthday by the ```!list_birthday``` command.
- [x] Change the database design and the bot logic so that one bot instance can be invited to multiple servers.
- [x] Create a channel dedicated for birthday celebration automatically when join a new server.
- [x] Doesn't reply to command that are not in the dedicated channel
- [x] Clean the data related to the server that kicked the bot or the bot left itself.
- [x] Create a categoty "activity" and create the channel under this category instead of globally in the server.