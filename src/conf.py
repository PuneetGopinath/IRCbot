"""
Copyright (c) 2021 BK IRCbot team and contributors

Licensed under GNU Lesser General Public License v2.1
See the LICENSE file distributed with the source code
OR Visit https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

This project is a fork of https://github.com/Orderchaos/LinuxAcademy-IRC-Bot

NOTE      This program is distributed in the hope that it will be useful - WITHOUT
           ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
           FITNESS FOR A PARTICULAR PURPOSE.
"""

server = "chat.freenode.net"  # Server to connect.
port = 6667  # Port to use when connecting
channel = ["#chan"]  # Array of channels to join.
botnick = ""  # Your bot's nickname.
adminnick = ""  # Your IRC nickname.
password = ""  # Your IRC bot's password.
exitcode = "Stop " + botnick  # The message we will use to stop the bot if sent by admin.
filename = "ircchat.log"  # Filename in which messages will be logged.
