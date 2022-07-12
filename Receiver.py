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
buf = np.zeros((Util.BUFFER_SIZE, 1), dtype='int16')
offset = 0
kill = False # Mutating booleans is atomic in python

class Receiver(Thread):
    def __init__(self, connection, address, offsetLocal):
        Thread.__init__(self)

        global firstTime
        global offset

        self.connection = connection
        self.address = address
        self.offset = offsetLocal

        self.decoder = op.Decoder(Util.SF, 1)


    def run(self):
        global lastFrame
        global buf
        global audioLock
        global kill
        while not kill:
            audioPacket = Util.receive(self.connection, self.address)
            #print("Output at %s : %s" % (audioPacket.getTimestamp(), audioPacket.buf), file=sys.stderr)
            if audioPacket.getFrame() + Util.TIME_TRAVEL < currentFrame:
                continue
            rawBuf = audioPacket.decode(self.decoder, Util.BS)
            #rawBuf = audioPacket.buf
            audioMat = np.ndarray((len(rawBuf)>>1, 1), dtype='int16', buffer=rawBuf)
            #print(audioMat)
            audioMatf32 = np.array(audioMat, dtype='f4')
            audioMatf32 *= (Util.clamp(audioPacket.getDistance(), Util.PEAK_DISTANCE, Util.SILENCE_DISTANCE) - Util.SILENCE_DISTANCE) * Util.VOLUME_SLOPE
            audioMat = np.array(audioMatf32, dtype='int16')
            with audioLock:
                tmpBuf1, tmpBuf2 = Util.sliceBufRepeating((audioPacket.getFrame() + Util.TIME_TRAVEL) % Util.BUFFER_SIZE, len(audioMat), buf)
                if len(tmpBuf2) == 0:
                    #print(len(audioMat))
                    tmpBuf1 += np.minimum(32767 - tmpBuf1, audioMat)
                else:
                    tmpBuf1 += np.minimum(32767 - tmpBuf1, audioMat[:len(tmpBuf1)])
                    tmpBuf2 += np.minimum(32767 - tmpBuf2, audioMat[len(tmpBuf1):])
                lastFrame = audioPacket.getFrame() + Util.TIME_TRAVEL
                #print(lastFrame)

def callback(outData, frames, timestamp, status):
    global lastFrame
    global buf
    global audioLock
    global offset
    global lastCallback
    global currentFrame
    if audioLock.acquire(timeout=frames/Util.SF):
        #print("%s %s" % (currentFrame, lastFrame))
        nowIdx = currentFrame % Util.BUFFER_SIZE
        tmpBuf1, tmpBuf2 = Util.sliceBufRepeating(lastCallback, nowIdx - lastCallback, buf)
        tmpBuf1[:] = np.zeros((len(tmpBuf1), 1), dtype='int16')
        tmpBuf2[:] = np.zeros((len(tmpBuf2), 1), dtype='int16')
        lastCallback = nowIdx
        if lastFrame < currentFrame:
            outData[:] = np.zeros((frames, 1), dtype='int16')
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
        outData[:] = np.zeros((frames, 1), dtype='int16')
    currentFrame += frames
        
