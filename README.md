# Twitch IRC Bot

A Twitch IRC Bot based on asynchronous programming (asyncio)
- Detects pyramids in the chat
- Tags the author of the pyramid

### Create a Twitch account for the bot

Create a Twitch account you will control with the bot: https://www.twitch.tv

The account nickname will be the name used by the bot.

Connect to twitch using the bot account and generate a chat token for the bot

https://www.twitchtools.com/chat-token

### Setup environment (Python 3.5+ required)

#### Windows
```
cd <project folder>
virtualenv .venv
.venv/Script/pip.exe install -r requirements.txt
```

#### Linux
```
cd <project folder>
virtualenv .venv
.venv/bin/pip install -r requirements.txt
```



### Create a ```cfg.py``` file

Create the file ```TwitchBot/cfg.py``` and fill it as follow:

```
# cfg.py
# Configurations variables

HOST = "irc.twitch.tv"
PORT = 6667
NICK = <bot nickname in lowercase>
PASS = <chat token>
CHAN = <channel the bot will be connected to in lowercase>
RATE = (20/30)  # messages per second

CHAT_RE = ":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)"
CHAT_URL = "https://tmi.twitch.tv/group/user/{user}/chatters".format(user=CHAN.lower())
MESSAGE_PYRAMID_COMPLETED = <message sent when someone does a complet pyramid>

```
### Run the bot

In the project folder, run:

#### Windows
```
.venv/Script/python.exe main.py
```

#### Linux
```
.venv/bin/python main.py
```
