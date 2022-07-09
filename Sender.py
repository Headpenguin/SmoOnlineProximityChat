from threading import *
import time

import sounddevice as sd
import opuslib as op

import Packets
import Util

SF = 48000 # Sampling frequency in hertz
FS = 20 # Frame size in milliseconds
BS = int(SF*FS/1000) # Block size in short ints

encoder = op.Encoder(SF, 1, op.APPLICATION_VOIP)

micCV = Condition() # The lock on this is simultaneously for the condition variable and buf
buf = b'' # Audio buffer

class Sender(Thread):
    def __init__(self, connection, address, offset):
        Thread.__init__(self)

        self.connection = connection
        self.address = address
        self.offset = offset

        self.packet = Packets.Voice(0, b'')
        
    def run(self):
        while(1):
            with micCV:
                micCV.wait()
                self.packet.reinit(time.time() + self.offset, buf)
                data = self.packet.pack()
                Util.send(self.connection, self.packet.pack(), self.address)
            
            

def callback(data, frames, timestamp, status):
    global buf
    global micCV
    if frames < BS:
        data += b'\0' * (BS - frames)
    res = encoder.encode(data[:BS], BS)
    if micCV.acquire(blocking=False):
        buf = res
        micCV.notify()
        micCV.release()

#with sd.RawInputStream(samplerate=SF, blocksize=BS, dtype='int16', channels=1, callback=callback):
    
