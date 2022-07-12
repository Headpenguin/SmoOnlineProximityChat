from threading import *

import sounddevice as sd
import opuslib as op

import Packets
import Util

micCV = Condition() # The lock on this is simultaneously for the condition variable and buf
buf = b'' # Audio buffer
#bufAdcTime = 0
kill = False # Mutating booleans is atomic in python
currentFrame = 0

class Sender(Thread):
    def __init__(self, connection, address, offset):
        Thread.__init__(self)

        self.connection = connection
        self.address = address
        self.offset = offset

        self.packet = Packets.Voice(0, b'')
        self.encoder = op.Encoder(Util.SF, 1, op.APPLICATION_VOIP)
        
    def run(self):
        global micCV
        global buf
        global kill
        global currentFrame
        #global bufAdcTime
        while not kill:
            with micCV:
                micCV.wait()
                res = self.encoder.encode_float(buf[:Util.BS*4], Util.BS)
                #res = buf[:Util.BS * 2]
                self.packet.reinit(currentFrame, res)
                #data = self.packet.pack()
                Util.send(self.connection, self.packet.pack(), self.address)
                #print(currentFrame)
            #print("Input at %s : %s" % (self.packet.getTimestamp(), self.packet.buf))
            
            

def callback(data, frames, timestamp, status):
    global buf
    global micCV
    global currentFrame
    #global bufAdcTime
    currentFrame += frames
    #print("callback %s" % currentFrame)
    if micCV.acquire(blocking=False):
        if frames < Util.BS:
            data += b'\0' * (Util.BS - frames) * 4
        buf = data
        #bufAdcTime = timestamp.inputBufferAdcTime * 1000000000
        micCV.notify()
        micCV.release()

#with sd.RawInputStream(samplerate=SF, blocksize=BS, dtype='int16', channels=1, callback=callback):
    
