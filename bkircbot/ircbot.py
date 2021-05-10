"""
Copyright (c) 2016 Linux Academy
Copyright (c) 2021 BK IRCbot team and contributors

Licensed under GNU Lesser General Public License v2.1
See the LICENSE file distributed with the source code
OR Visit https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

This project is a fork of https://github.com/Orderchaos/LinuxAcademy-IRC-Bot

NOTE      This program is distributed in the hope that it will be useful - WITHOUT
           ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
           FITNESS FOR A PARTICULAR PURPOSE.
"""

# socket for irc socket
import socket

# os for file handling, currently not required
# import os

# import contextmanager from contextlib for protecting socket with context manager
from contextlib import contextmanager

# conf
from conf import server, port, channel, botnick, adminnick, password, exitcode, filename

# sys
import sys

if adminnick == "" or botnick == "":
    print(
        "Fatal Error: BK IRCbot: adminnick or botnick is empty! " +
        "Please update the configuration and restart the bot."
    )
    sys.exit()


@contextmanager
def socketcontext(*args, **kw):
    ircsock = socket.socket(*args, **kw)
    try:
        yield ircsock
    finally:
        ircsock.close()


# Create a socket
with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as ircsock:

    ircsock.connect((server, port))  # Here we connect to the server
    # We need to send some info to the server to let the server identify us.
    # user information - USER <username> <hostname> <servername> :<realname>
    ircsock.send((
        f"USER {botnick} {botnick} {botnick} "
        f":IRCbot by Linux Academy and Puneet Gopinath.\n"
    ).encode("UTF-8"))
    # tell the bot's nick to the server
    ircsock.send((
        f"NICK {botnick} \n"
    ).encode("UTF-8"))
    # identify the bot's IRC account
    ircsock.send((
        "NickServ identify " + password + "\n"
    ).encode("UTF-8"))

    def join_channel(chan):
        """Join channel(s)

        Parameters:
        chan (string): Channel(s) to join. Seperate a channel using a comma, e.g. #chan,#chan2

        Returns:
        null: Returns null.
        """
        # The `encode("UTF-8")` says to send the message to IRC as UTF-8 encoded bytes.
        ircsock.send((f"JOIN {chan} \n").encode("UTF-8"))
        # The "\n” at the end of the line denotes to send a new line character.
        # After sending the join command, we start a loop
        # To continuously check and receive new info from server
        # UNTIL we get a message from the server ‘End of /NAMES list.’.
        # This will indicate we have successfully joined the channel.
        # The details of how each function works is described in the main function section below.
        # This is necessary so we don't process the joining message as commands.
        ircmsg = ""
        while ircmsg.find("End of /NAMES list.") == -1:
            ircmsg = ircsock.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip("\n\r")
            print(ircmsg)

    def ping():
        """If the server send a ping to us, respond with a pong.

        Returns:
        null: Returns null.
        """
        ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

    def sendmsg(msg, target):
        """Send a message to a channel or some nick

        Parameters:
        msg (string): The message.
        target (string): Send message to which channel/nick?

        Returns:
        null: Returns null.
        """
        # Here we are sending a PRIVMSG to the server.
        # The " :" lets the server separate the target and the message.
        ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

    def logger(name, msg):
        """Log message

        Parameters:
        name (string): Name to person who sent the message
        msg (string): The message.

        Returns:
        null: Returns null.
        """
        irclog = open(filename, "r")
        content = irclog.readlines()[:-100]
        irclog.close()

        irclog = open(filename, "w")
        if len(content) > 0:
            for i in content:
                irclog.write(i.strip("\n\r") + "\n")
        # write newest message to log.
        irclog.write(name + ":" + msg.strip("\n\r") + "\n")
        irclog.close()

    def start():
        """Start the bot

        Returns:
        null: Returns null.
        """
        # start by joining the channel(s) we defined.
        chan = ""
        for x in channel:
            chan += x + ","
        join_channel(chan)
        # Start infinite loop to keep checking and receive new info from server.
        # This ensures our connection stays open.
        # An infinite while loop works better in this case.
        while 1:
            # Here we are receiving information from the IRC server.
            # Tell our socket to receive up to 2048 bytes and decode it as UTF-8 characters.
            # We then assign it to the ircmsg variable for processing.
            ircmsg = ircsock.recv(2048).decode("UTF-8")
            # This part will remove any line break characters from the string.
            ircmsg = ircmsg.strip("\n\r")
            # This will print the received information to your terminal.
            # Useful for debugging purposes
            print(ircmsg)
            # Here we check if the information we received was a PRIVMSG.
            # PRIVMSG is standard messages sent to the channel or direct messages sent to the bot.
            # Most of the processing of messages will be in this section.
            if ircmsg.find("PRIVMSG") != -1:
                # Messages come from IRC in the format of
                # ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]"
                name = ircmsg.split("!", 1)[0][1:]
                # message.
                message = ircmsg.split("PRIVMSG", 1)[1].split(" :", 1)[1]
                # To whom (or to which channel) it was sent.
                sentTo = ircmsg.split("PRIVMSG", 1)[1].split(" :", 1)[0].lstrip()
                if (sentTo.lower() == botnick.lower()):
                    sendTo = name
                else:
                    sendTo = sentTo
                # Log the message
                logger(name, "(Sent To: " + sentTo + ") :" + message)
                # We check if the name is less than 17 characters.
                # Nicks (at least for Freenode) are limited to 16 characters.
                admin = name.lower() == adminnick.lower()
                if len(name) < 17:
                    if message.find("Hi " + botnick) != -1 or message.find("Who is " + botnick) != -1:
                        sendmsg("Hello " + name + "!", sendTo)
                        sendmsg(
                            "I am a bot created by PuneetGopinath, " +
                            "initialy developed by Linux Academy. " +
                            "Please report any issues at " +
                            "https://github.com/PuneetGopinath/IRCbot/issues",
                            sendTo
                        )
                    if admin and message.rstrip() == "Clear the file, " + botnick:
                        sendmsg("Ok, will clear the file.", sendTo)
                        irclog = open(filename, "w")
                        irclog.write("")
                        irclog.close()
                    # Here we add in some code to help us get the bot to stop.
                    # Check whether the name of the person sending the msg matches the admin nick.
                    # We make sure the message EXACTLY matches the exit code above.
                    # The only adjustment here is to trim at the right end of the message.
                    if admin and message.rstrip() == exitcode:
                        sendmsg(
                            "Bye... 😭 Waiting to see you again!!",
                            sendTo
                        )
                        # Send the quit command to the IRC server so it knows we’re leaving.
                        ircsock.send(bytes("QUIT \n", "UTF-8"))
                        # The return command ends the function here
                        # So the bot stops
                        return
            # If the message is not a PRIVMSG it still might need some response.
            else:
                # Check if the info we received was a PING request.
                # If yes, we call the ping() function so we respond with a PONG to the server.
                if ircmsg.find("PING :") != -1:
                    ping()

    # The main function is defined, we need to start it.
    start()
