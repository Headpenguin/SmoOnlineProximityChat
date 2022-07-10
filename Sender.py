from threading import *
import time

import sounddevice as sd
import opuslib as op

import Packets
import Util

micCV = Condition() # The lock on this is simultaneously for the condition variable and buf
buf = b'' # Audio buffer

class Sender(Thread):
    def __init__(self, connection, address, offset):
        Thread.__init__(self)

        self.connection = connection
        self.address = address
        self.offset = offset

        self.packet = Packets.Voice(0, b'')
        self.encoder = op.Encoder(Util.SF, 1, op.APPLICATION_VOIP)
        
    def run(self):
        while(1):
            with micCV:
                micCV.wait()
                if frames < Util.BS:
                    data += b'\0' * (Util.BS - frames)
                res = self.encoder.encode(data[:Util.BS], Util.BS)
                self.packet.reinit(time.time() + self.offset, res)
                data = self.packet.pack()
                Util.send(self.connection, self.packet.pack(), self.address)
            
            

def callback(data, frames, timestamp, status):
    global buf
    global micCV
    if micCV.acquire(blocking=False):
        buf = data
        micCV.notify()
        micCV.release()

#with sd.RawInputStream(samplerate=SF, blocksize=BS, dtype='int16', channels=1, callback=callback):
    
