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
import threading

#import numpy as np
import sounddevice as sd
import ntplib as ntp

import Packets
import Util
import Sender
import Receiver


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

offset = 0
kill = False # Mutating booleans is atomic in python

#try:
    #offset = ntp.NTPClient().request("pool.ntp.org").offset
#except ntp.NTPException:
  #  print("Could not sync time with time server, proceeding without a synchronised time", file=sys.stderr)

address = (IP, PORT)

first = Packets.Connect(NAME)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connectionRecv, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connectionSend:

    while not Util.send(connectionRecv, first.pack(), address):
        pass
    #Util.send(connection, first.pack(), address)

    response = Util.receive(connectionRecv, address)
    response.setGUID()

    Util.SILENCE_DISTANCE = response.silenceDistance
    Util.PEAK_DISTANCE = response.peakDistance
    currentFrame = response.currentFrame

    sender = Sender.Sender(connectionSend, address, offset)
    sender.start()

    Receiver.currentFrame = currentFrame
    Sender.currentFrame = currentFrame

    receiver = Receiver.Receiver(connectionRecv, address, offset)
    receiver.start()

    def gigaCallback(indata, outdata, frames, timestamp, status):
        Sender.callback(indata.tobytes(), frames, timestamp, status)
        Receiver.callback(outdata, frames, timestamp, status)

    def run():
        with sd.Stream(samplerate=Util.SF, blocksize=Util.BS, dtype='int16', channels=1, callback=gigaCallback):
            while not kill:
                time.sleep(5)

    thread = threading.Thread(target=run)
    thread.start()
    #input("Type anything to exit\n")
    time.sleep(9)
    print("Closing...")

    Sender.kill = True
    Receiver.kill = True

    sender.join(timeout=1)
    if sender.is_alive():
        print("Forcefully closing recording...")
    receiver.join(timeout=1)
    if receiver.is_alive():
        print("Forcefully closing audio playback...")

    kill = True
    thread.join(timeout=5.5)
    if thread.is_alive():
        print("Forcefully killing this chat client...")


