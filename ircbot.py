#!/usr/bin/python3

# Copyright (c) 2016-2021 Linux Academy, Puneet Gopinath
# license   https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html GNU Lesser General Public License v2.1
# credits to Linux Academy, forked from https://github.com/Orderchaos/LinuxAcademy-IRC-Bot
# note      This program is distributed in the hope that it will be useful - WITHOUT
#           ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#           FITNESS FOR A PARTICULAR PURPOSE.

import socket
#This first variable is the socket we’ll be using to connect and communicate with the IRC server. Sockets are complicated and can be used for many tasks in many ways.
#See here if you’d like more information on sockets: https://docs.python.org/3/howto/sockets.html.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "chat.freenode.net" # Server
channel = "#chan" # Channel
botnick = "puneetBot" # Your bot's nick.
adminnick = "puneetgopi" #Your IRC nickname.
password = "" #Your IRC bot's password
exitcode = "Stop " + botnick #The content of message we will use to stop the bot if sent by admin
filename = "ircchat.log" #Filename in which messages will be stored

#To connect to IRC we need to use our socket variable (ircsock) and connect to the server.
#We need to have the server name (established in our Global Variables) and the port number inside parentheses so it gets passed as a single item to the connection.
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
#Once we’ve established the connection we need to send some information to the server to let the server know who we are.
# USER <username> <hostname> <servername> :<realname>
ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " :IRCbot by Linux Academy and Puneet Gopinath.\n", "UTF-8")) # user information
ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8")) # assign the nick to the bot
ircsock.send(bytes("NickServ identify " + password + "\n", "UTF-8")) # identify the nick
def joinchan(chan):

  #The ‘bytes’ part and "UTF-8” says to send the message to IRC as UTF-8 encoded bytes. In Python 2 this isn’t necessary, but changes to string encoding in Python 3 makes this a requirement here.
  #You will see this on all the lines where we send data to the IRC server.
  ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))
  #Something to note, the "\n” at the end of the line denotes to send a new line character. It lets the server know we’re finished with that command rather than chaining all the commands onto the same line.
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
#All we need for this function is to accept a variable with the message we’ll be sending and who we’re sending it to. We will assume we are sending to the channel by default if no target is defined.
#Using target=channel in the parameters section says if the function is called without a target defined, example below in the Main Function section, then assume the target is the channel.
# sends messages to the target (by default channel).
def sendmsg(msg, target=channel):
  #With this we are sending a ‘PRIVMSG’ to the channel. The " :" lets the server separate the target and the message.
  ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))
def logger(name, msg):
  # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
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
  # start by joining the channel we defined in the Global Variables section.
  joinchan(channel)
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
      #First we want to get the nick of the person who sent the message. Messages come in from from IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
      #We need to split and parse it to analyze each part individually.
      name = ircmsg.split("!",1)[0][1:]
      #Here we split out the message.
      message = ircmsg.split("PRIVMSG",1)[1].split(" :",1)[1]
      #Here we split out the sentTo (to understand whether it was sent to channel or sent to botnick privately).
      sentTo = ircmsg.split("PRIVMSG",1)[1].split(" :",1)[0]
      #Log the message
      logger(name, "(sentTo: " + sentTo + ") :" + message)
      #Now that we have the name information, we check if the name is less than 17 characters. Nicks (at least for Freenode) are limited to 16 characters.
      if len(name) < 17:
        if message.find("Hi " + botnick) != -1 or message.find("Who is " + botnick) != -1:
          sendmsg("Hello " + name + "!")
          sendmsg("I am a bot created by PuneetGopinath, I record messages sent to a channel and save it to a file, bot can be started in their servers (or command line) and it will record messages. Credits to Linux Academy and PuneetGopinath.")
        if name.lower() == adminnick.lower() and message.rstrip() == "Clear the file, " + botnick:
          sendmsg("Ok, will clear the file.")
          irclog = open(filename, "w")
          irclog.write("")
          irclog.close()
        #Here we add in some code to help us get the bot to stop. Since we created an infinite loop, there is no normal ‘end’.
        #Instead, we’re going to check for some text and use that to end the function (which automatically ends the loop).
        #Look to see if the name of the person sending the message matches the admin name we defined earlier. We make both lower case in case the admin typed their name a little differently when joining.
        #We also make sure the message matches the exit code above. The exit code and the message must be EXACTLY the same. This way the admin can still type the exit code with extra text to explain it or talk about it to other users and it won’t cause the bot to quit.
        #The only adjustment we're making is to trim off any whitespace at the end of the message. So if the message matches, but has an extra space at the end, it will still work.
        if name.lower() == adminnick.lower() and message.rstrip() == exitcode:
          #If we do get sent the exit code, then send a message (no target defined, so to the channel) saying we’ll do it, but making clear we’re sad to leave.
          sendmsg("Okay. I will stop.")
          #Send the quit command to the IRC server so it knows we’re disconnecting.
          ircsock.send(bytes("QUIT \n", "UTF-8"))
          #The return command returns to when the function was called (we haven’t gotten there yet, see below) and continues with the rest of the script.
          #In our case, there is not any more code to run through so it just ends.
          return
    #If the message is not a PRIVMSG it still might need some response.
    else:
      #Check if the information we received was a PING request. If so, we call the ping() function we defined earlier so we respond with a PONG.
      if ircmsg.find("PING :") != -1:
        ping()
#Finally, now that the main function is defined, we need to start it.
main()
