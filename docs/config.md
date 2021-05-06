<h2 align="center">BK IRCbot Docs - Configuring settings</h2>

<link rel="stylesheet" href="https://puneetgopinath.github.io/css/main.css" />

To Configure BK IRCbot read this guide.

The list of all settings are below:

## 1. server

Default `chat.freenode.net`. The server to connect.

## 2. port

The port to use to connect to the server. Defaults to `6667`

Use ports `6697` or `7000` or `7070` for TLS connection.

## 2. channel

The channels to join, it's an array of channel name with `#` to join for recording IRC messages.

Example:
```py
channel = ["#chan", "#chan2"]
```

## 3. botnick

The nick name to the bot. This should be registered to the server defined above.
You can just connect to your IRC server with a client and then send `/nick yournick` where yournick is your nickname you want to register.
And then send `/msg NickServ register youremail password`

If you don't want to download IRC client, you can visit [webchat.freenode.net](https://webchat.freenode.net) to register your nickname if you would like to use freenode.

See [here](https://en.wikipedia.org/wiki/Wikipedia:IRC/Tutorial#Nickname_registration) for more information on Nickname registration

## 4. adminnick

Your irc nick.
As mentioned above, it should also be registered.

## 5. password

The password of the bot's nick.

## 6. exitcode

The message to send for the bot to stop.

By default if you send `Stop botnick`, where botnick is nick specified in config setting 2.

---------------------------------------------------------------------

You have to edit these config settings after opening `src/conf.py`

---------------------------------------------------------------------

[Back to home](README.md)
