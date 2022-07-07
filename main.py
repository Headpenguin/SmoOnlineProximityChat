#! /usr/bin/python3


''' |
    v''' 
NAME = "Sussy 1" # Modify this to change your in-game name
IP = "127.0.0.1" # Modify this to set the server ip address
PORT = None # Modify this to set the server port number
'''^
   |'''


import os
import sys
import time
import socket

import numpy as np
import sounddevice as sd

import Packets

TIME_TRAVEL = 25 # How long we wait to play back audio we recieve, in milliseconds
SILENCE_DISTANCE = 10 # The farthest a player can be and still be heard (this is the default, the actual value is loaded from the server)
PEAK_DISTANCE = 3 # How close a player must be to be heard at the maximum volume (this is the default, the actual value is loaded from the server)

def send(connection, data, address):
    total = connection.sendto(data[0], address)
    total += connection.sendto(data[1], address)
    if total < len(data[0]) + len(data[1]):
        return False
    return True

def receive(connection, expectedAddress):
    data, address = (None, None)
    while address != expectedAddress:
        data, address = connection.recvfrom(Packets.HEADER_LEN)
    header = Packets.Header.unpack(data)
    data, address = (None, None)
    while address != expectedAddress:
        data, address = connection.recvfrom(header.size)
    packet = Packets.PACKET_TYPE_TABLE[header.ty].unpack(header, data)
    return packet
    

if NAME != None:
    pass
elif len(sys.argv) > 1:
    NAME = sys.argv[1]
elif "IN_GAME_NAME" in os.environ.keys():
    NAME = os.environ["IN_GAME_NAME"]
else:
    print("No name has been provided, so proximity chat cannot function. Please provide a name in one of the following ways:", file=sys.stderr)
    print("    1. Provide your name as the first argument to this Python script. For example, enter `python3 proximity-chat.py myUser_nameIs-reallyc0ol ipAddress` into your command prompt.", file=sys.stderr)
    print("    2. Put you name into the environment variable IN_GAME_NAME.", file=sys.stderr)
    print("    3. Enter your name directly into this script. To do so, open this file (proximity-chat.py), and to the right of the `=` sign next to the variable called `NAME` near the top of the file, type your desired name and surround it \
with quotes. For example, change the line `NAME = None` to `NAME = 'MyUserNameIsReallyEpic'`.", file=sys.stderr)
    print("Make sure that your username matches your in-game username, or else this program will not function", file=sys.stderr)
    print("Now exiting")
    sys.exit(-1)

if IP != None:
    pass
elif "SMO_HOST_SERVER_IP" in os.environ.keys():
    IP = os.environ["SMO_HOST_SERVER_IP"]
elif len(sys.argv) > 1:
    IP = sys.argv[-1]
else:
    print("No ip has been provided, so proximity chat cannot function. Please provide an ip in one of the following ways:", file=sys.stderr)
    print("    1. Provide your host server's ip as the final argument to this Python script. For example, enter `python3 proximity-chat.py myUser_nameIs-reallyc0ol ipAddress` into your command prompt.", file=sys.stderr)
    print("    2. Put you ip into the environment variable SMO_HOST_SERVER_IP.", file=sys.stderr)
    print("    3. Enter your name directly into this script. To do so, open this file (proximity-chat.py), and to the right of the `=` sign next to the variable called `IP` near the top of the file, type your host server's ip and surround it \
with quotes. For example, change the line `IP = None` to `IP = '123.45.67.89'`.", file=sys.stderr)
    print("Make sure that the ip you enter matches your host server's ip, or else this program will not be able to connect to the server", file=sys.stderr)
    print("Now exiting")
    sys.exit(-1)

if PORT != None:
    pass
elif "SMO_HOST_SERVER_PORT" in os.environ.keys():
    PORT = int(os.environ["SMO_HOST_SERVER_PORT"])
elif len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[-1])
    except ValueError:
        if len(sys.argv) > 2:
            try:
                PORT = int(sys.argv[-2])
            except ValueError:
                pass
else:
    PORT = 48984
    print("No port has been provided, so proximity chat cannot function. Please provide a port in one of the following ways:", file=sys.stderr)
    print("    1. Provide your host server's port as the second-to-last argument to this Python script. For example, enter `python3 proximity-chat.py myUser_nameIs-reallyc0ol portNumber ipAddress` into your command prompt.", file=sys.stderr)
    print("    2. Put your port into the environment variable SMO_HOST_SERVER_PORT.", file=sys.stderr)
    print("    3. Enter your port directly into this script. To do so, open this file (proximity-chat.py), and to the right of the `=` sign next to the variable called `PORT` near the top of the file, type your host server's port number. \
For example, change the line `PORT = None` to `PORT = 12345'`.", file=sys.stderr)
    print("Make sure that the port you enter matches your host server's port, or else this program will not be able to connect to the server", file=sys.stderr)
    print("Resuming execution, defaulting port to 48984", file=sys.stderr)
          
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = (IP, PORT)

first = Packets.Connect(NAME)

while not send(connection, first.pack(), address):
    pass

response = receive(connection, address)

response.setGUID()

SILENCE_DISTANCE = response.silenceDistance
PEAK_DISTANCE = response.peakDistance

#header = Packets.Packet(connection.recv(Packets.HEADER_LEN))

t = np.linspace(0, 3, 3 * 44100, False)

audio1 = np.sin(440 * t * 2 * np.pi)

audio2 = np.sin(660 * t * 2 * np.pi)

sd.play(audio1, 44100)

time.sleep(1)

sd.play(audio2, 44100)
