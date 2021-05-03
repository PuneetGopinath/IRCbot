#!/usr/bin/python3

# Copyright (c) 2016 Linux Academy
# Copyright (c) 2021 Puneet Gopinath
#
# Licensed under GNU Lesser General Public License v2.1
# See the LICENSE file OR Visit https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
#
# This project is a fork of https://github.com/Orderchaos/LinuxAcademy-IRC-Bot
#
# NOTE      This program is distributed in the hope that it will be useful - WITHOUT
#           ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#           FITNESS FOR A PARTICULAR PURPOSE.

# socket for irc socket
import socket
# os for file handling
import os

# Create a socket
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "chat.freenode.net" # Server to connect.
channel = ["#chan"] # Array of channels to join.
botnick = "" #Your bot's nickname.
adminnick = "" #Your IRC nickname.
password = "" #Your IRC bot's password.
exitcode = "Stop " + botnick #The content of message we will use to stop the bot if sent by admin.
filename = "ircchat.log" #Filename in which messages will be logged.

if adminnick == "" or botnick == "":
    print("Note: adminnick or botnick is empty!")

ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
#We need to send some info to the server to let the server identify us.
# USER <username> <hostname> <servername> :<realname>
ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " :IRCbot by Linux Academy and Puneet Gopinath.\n", "UTF-8")) # user information
ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8")) # assign the nick to the bot
ircsock.send(bytes("NickServ identify " + password + "\n", "UTF-8")) # login to the botnick's IRC account

def joinchan(chan):
    #The ‘bytes’ part and "UTF-8” says to send the message to IRC as UTF-8 encoded bytes. In Python 2 this isn’t necessary, but changes to string encoding in Python 3 makes this a requirement here.
    #You will see this on all the lines where we send data to the IRC server.
    ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))
    #The "\n” at the end of the line denotes to send a new line character. It tells the server that we’re finished with that command rather than chaining all the commands onto the same line.
    # After sending the join command, we want to start a loop to continually check for and receive new info from server until we get a message with ‘End of /NAMES list.’.
    #This will indicate we have successfully joined the channel. The details of how each function works is described in the main function section below.
    #This is necessary so we don't process the joining message as commands.
    ircmsg = ""
    while ircmsg.find("End of /NAMES list.") == -1:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip("\n\r")
        print(ircmsg)

def ping():
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

#All we need for this function is to accept a variable with the message we’ll be sending and who we’re sending it to.
# sends messages to the target
def sendmsg(msg, target):
    #With this we are sending a ‘PRIVMSG’ to the channel. The " :" lets the server separate the target and the message.
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

def logger(name, msg):
    irclog = open(filename, "r")
    content = irclog.readlines()
    irclog.close()
    # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
    irclog = open(filename, "w")
    while len(content) > 100:
        content.remove(content[0])
    if len(content) > 0:
        for i in content:
            irclog.write(i.strip("\n\r") + "\n")
    # write newest messge to log.
    irclog.write(name + ":" + msg.strip("\n\r") + "\n")
    irclog.close()

def main():
    # start by joining the channel(s) we defined.
    chan = ""
    for x in channel:
        chan += x + ","
    joinchan(chan)
    #Start infinite loop to continually check for and receive new info from server. This ensures our connection stays open.
    #An infinite while loop works better in this case.
    while 1:
        #Here we are receiving information from the IRC server. IRC will send out information encoded in UTF-8 characters so we’re telling our socket connection to receive up to 2048 bytes and decode it as UTF-8 characters.
        #We then assign it to the ircmsg variable for processing.
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        # This part will remove any line break characters from the string. If someone types in "\n” to the channel, it will still include it in the message just fine.
        ircmsg = ircmsg.strip("\n\r")
        #This will print the received information to your terminal. You can skip this if you don’t want to see it, but it helps with debugging and to make sure your bot is working.
        print(ircmsg)
        #Here we check if the information we received was a PRIVMSG. PRIVMSG is how standard messages in the channel (and direct messages to the bot) will come in.
        #Most of the processing of messages will be in this section.
        if ircmsg.find("PRIVMSG") != -1:
            #Messages come from IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
            name = ircmsg.split("!",1)[0][1:]
            #Split out the message.
            message = ircmsg.split("PRIVMSG",1)[1].split(" :",1)[1]
            #Split out the sentTo (to understand whether it was sent to channel or sent to botnick privately).
            sentTo = ircmsg.split("PRIVMSG",1)[1].split(" :",1)[0].lstrip()
            if (sentTo.lower() == botnick.lower()):
                sendTo = name
            else:
                sendTo = sendTo
            #Log the message
            logger(name, "(Sent To: " + sentTo + ") :" + message)
            #Now that we have the name information, we check if the name is less than 17 characters. Nicks (at least for Freenode) are limited to 16 characters.
            if len(name) < 17:
                if message.find("Hi " + botnick) != -1 or message.find("Who is " + botnick) != -1:
                    sendmsg("Hello " + name + "!", sendTo)
                    sendmsg("I am a bot created by PuneetGopinath initialy developed by Linux Academy. Credits to Linux Academy and PuneetGopinath. Please report any issues at https://github.com/PuneetGopinath/IRCbot/issues", sendTo)
                if name.lower() == adminnick.lower() and message.rstrip() == "Clear the file, " + botnick:
                    sendmsg("Ok, will clear the file.", sendTo)
                    irclog = open(filename, "w")
                    irclog.write("")
                    irclog.close()
                #Here we add in some code to help us get the bot to stop. Since we created an infinite loop.
                #Check whether the name of the person sending the message matches the admin name we defined earlier. We make both lower case in case the admin typed their name a little differently when joining.
                #We make sure the message matches the exit code above. The exit code and the message must be EXACTLY the same. This way the admin can still type the exit code with extra text to explain it or talk about it to other users and it won’t cause the bot to quit.
                #The only adjustment we're making is to trim off any whitespace at the right side of the message.
                if name.lower() == adminnick.lower() and message.rstrip() == exitcode:
                    #If we do get sent the exit code, then send a message (target is from were we received) saying we’ll do it.
                    sendmsg("Okay. Bye... 😭", sendTo)
                    #Send the quit command to the IRC server so it knows we’re disconnecting.
                    ircsock.send(bytes("QUIT \n", "UTF-8"))
                    #The return command returns to when the function was called (we haven’t gotten there yet, see below) and continues with the rest of the script.
                    #In our case, there is not any more code to run through so it just ends.
                    return
        #If the message is not a PRIVMSG it still might need some response.
        else:
            #Check if the info we received was a PING request. If yes, we call the ping() function we defined earlier so we respond with a PONG to the server.
            if ircmsg.find("PING :") != -1:
                ping()
#The main function is defined, we need to start it.
main()
