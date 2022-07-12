from threading import *

import sounddevice as sd
import opuslib as op

import Packets
import Util

micCV = Condition() # The lock on this is simultaneously for the condition variable and buf
buf = b'' # Audio buffer
kill = False # Mutating booleans is atomic in python
currentFrame = 0

class Sender(Thread):
    def __init__(self, connection, address):
        Thread.__init__(self)

        self.connection = connection
        self.address = address

        self.packet = Packets.Voice(0, b'')
        self.encoder = op.Encoder(Util.SF, 1, op.APPLICATION_VOIP)
        
    def run(self):
        global micCV
        global buf
        global kill
        global currentFrame
        while not kill:
            with micCV:
                micCV.wait()
                res = self.encoder.encode_float(buf[:Util.BS*4], Util.BS)
                self.packet.reinit(currentFrame, res)
                Util.send(self.connection, self.packet.pack(), self.address)
            
def callback(data, frames, timestamp, status):
    global buf
    global micCV
    global currentFrame
    currentFrame += frames
    if micCV.acquire(blocking=False):
        if frames < Util.BS:
            data += b'\0' * (Util.BS - frames) * 4
        buf = data
        micCV.notify()
        micCV.release()
        
