from threading import *
import time

import sounddevice as sd
import opuslib as op
import numpy as np

import Packets
import Util

audioLock = Lock()
timestamps = {}
firstTime = time.time()
lastTime = 0
buf = np.zeros((Util.BUFFER_SIZE, 1), dtype='int16')


class Receiver(Thread):
    def __init__(self, connection, address, offset):
        Thread.__init__(self)

        self.connection = connection
        self.address = address
        self.offset = offset

        self.decoder = op.Decoder(Util.SF, 1)

        firstTime += offset

    def run(self):
        while(1):
            audioPacket = receive(self.connection, self.address)
            if audioPacket.getTimestamp() + Util.TIME_TRAVEL < time.time() + offset:
                continue
            rawBuf = audioPacket.decode(self.decoder, Util.BS)
            audioMat = np.ndarray((len(rawBuf), 1), dtype='int16', buffer=rawBuf)
            audioMat *= Util.clamp(audioPacket.getDistance(), Util.PEAK_DISTANCE, Util.SILENCE_DISTANCE) - Util.SILENCE_DISTANCE) * Util.VOLUME_SLOPE
            with audioLock:
                tmpBuf1, tmpBuf2 = Util.sliceBufRepeating(Util.timestampToIndex(firstTime, (audioPacket.getTimestamp() + Util.TIME_TRAVEL ), Util.SF) % Util.BUFFER_SIZE, len(rawBuf), buf)
                if tmpBuf2 == None:
                    tmpBuf1 += np.minimum(32767 - tmpBuf1, audioMat)
                else:
                    tmpBuf1 += np.minimum(32767 - tmpBuf1, audioMat[:len(tmpBuf1)])
                    tmpBuf2 += np.minimum(32767 - tmpBuf2, audioMat[len(tmpBuf1):])
                lastTime = audioPacket.getTimestamp() + Util.TIME_TRAVEL

def callback(outdata, frames, timestamp, status):
    if audioLock.acquire(timeout=frames/Util.SF):
        now = time.time() + offset
        if lastTime < now:
            outdata[:] = np.zeros((frames, 1), dtype='int16')
        else:
            tmpBuf1, tmpBuf2 = Util.sliceBufRepeating(Util.timestampToIndex(firstTime, now, Util.SF) % Util.BUFFER_SIZE, frames, buf)
            if tmpBuf2 == None:
                outData[:] = tmpBuf1
            else:
                outData[:len(tmpBuf1)] = tmpBuf1
                outData[len(tmpBuf1):] = tmpBuf2
        audioLock.release()
    else:
        outdata[:] = np.zeros((frames, 1), dtype='int16')
        
