from threading import *
import sys

import sounddevice as sd
import opuslib as op
import numpy as np

import Packets
import Util

audioLock = Lock()
currentFrame = 0
lastFrame = 0
lastCallback = 0
buf = np.zeros((Util.BUFFER_SIZE, 1), dtype='float32')
kill = False # Mutating booleans is atomic in python

class Receiver(Thread):
    def __init__(self, connection, address):
        Thread.__init__(self)

        global firstTime

        self.connection = connection
        self.address = address

        self.decoder = op.Decoder(Util.SF, 1)


    def run(self):
        global lastFrame
        global buf
        global audioLock
        global kill
        while not kill:
            audioPacket = Util.receive(self.connection, self.address)
            #print(audioPacket.header.size)
            #print("Output at %s : %s" % (audioPacket.getTimestamp(), audioPacket.buf), file=sys.stderr)
            if audioPacket.getFrame() + Util.TIME_TRAVEL < currentFrame:
                continue
            rawBuf = bytearray(audioPacket.decode_float(self.decoder, Util.BS))
            #rawBuf = audioPacket.buf
            audioMat = np.ndarray((len(rawBuf)>>2, 1), dtype='float32', buffer=rawBuf)
            audioMat *= (Util.clamp(audioPacket.getDistance(), Util.PEAK_DISTANCE, Util.SILENCE_DISTANCE) - Util.SILENCE_DISTANCE) * Util.VOLUME_SLOPE
            
            with audioLock:
                tmpBuf1, tmpBuf2 = Util.sliceBufRepeating((audioPacket.getFrame() + Util.TIME_TRAVEL) % Util.BUFFER_SIZE, len(audioMat), buf)
                if len(tmpBuf2) == 0:
                    #print(len(audioMat))
                    tmpBuf1 += audioMat
                else:
                    tmpBuf1 += audioMat[:len(tmpBuf1)]
                    tmpBuf2 += audioMat[len(tmpBuf1):]
                lastFrame = audioPacket.getFrame() + Util.TIME_TRAVEL
                #print(lastFrame)

def callback(outData, frames, timestamp, status):
    global lastFrame
    global buf
    global audioLock
    global lastCallback
    global currentFrame
    if audioLock.acquire(timeout=frames/Util.SF):
        #print("%s %s" % (currentFrame, lastFrame))
        nowIdx = currentFrame % Util.BUFFER_SIZE
        tmpBuf1, tmpBuf2 = Util.sliceBufRepeating(lastCallback, (nowIdx - lastCallback) % Util.BUFFER_SIZE, buf)
        tmpBuf1[:] = np.zeros((len(tmpBuf1), 1), dtype='float32')
        tmpBuf2[:] = np.zeros((len(tmpBuf2), 1), dtype='float32')
        lastCallback = nowIdx
        if lastFrame < currentFrame:
            outData[:] = np.zeros((frames, 1), dtype='float32')
        else:
            #print("%s - %s" % (nowIdx, nowIdx + frames))
            tmpBuf1, tmpBuf2 = Util.sliceBufRepeating(nowIdx, frames, buf)
            if len(tmpBuf2) == 0:
                outData[:] = tmpBuf1
            else:
                outData[:len(tmpBuf1)] = tmpBuf1
                outData[len(tmpBuf1):] = tmpBuf2
        audioLock.release()
    else:
        outData[:] = np.zeros((frames, 1), dtype='float32')
    currentFrame += frames
        
