#! /usr/bin/python3


''' |
    v''' 
NAME = "Test" # Modify this to change your in-game name
'''^
   |'''


import os
import sys
import time
import numpy as np
import sounddevice as sd

TIME_TRAVEL = 25 # How long we wait to play back audio we recieve, in milliseconds
SILENCE_DISTANCE = 10 # The farthest a player can be and still be heard
PEAK_DISTANCE = 3 # How close a player must be to be heard at the maximum volume

if NAME != None:
    pass
elif len(sys.argv) > 1:
    NAME = sys.argv[1]
elif "IN_GAME_NAME" in os.environ.keys():
    NAME = os.environ["IN_GAME_NAME"]
else:
    print("No name has been provided, so proximity chat cannot function. Please provide a name in one of the following ways:", file=sys.stderr)
    print("    1. Provide your name as an argument to this Python script. For example, enter `python3 proximity-chat.py myUser_nameIs-reallyc0ol` into your command prompt.", file=sys.stderr)
    print("    2. Put you name into the environment variable IN_GAME_NAME.", file=sys.stderr)
    print("    3. Enter your name directly into this script. To do so, open this file (proximity-chat.py), and to the right of the `=` sign next to the variable called `NAME` near the top of the file, type your desired name and surround it \
with quotes. For example, change the line `NAME = None` to `NAME = 'MyUserNameIsReallyEpic'`.", file=sys.stderr)
    print("Make sure that your username matches your in-game username, or else this program will not function", file=sys.stderr)
    print("Now exiting")
    sys.exit(-1)

t = np.linspace(0, 3, 3 * 44100, False)

print("%s, %s, %s, %s, %s, %s, %s, %s" %(t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7]))

audio1 = np.sin(440 * t * 2 * np.pi)

audio2 = np.sin(660 * t * 2 * np.pi)

sd.play(audio1, 44100)

time.sleep(1)

sd.play(audio2, 44100)

print(NAME)
