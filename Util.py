import socket
import math

import numpy as np

import Packets

SF = 48000 # Sampling frequency in hertz
FS = 20 # Frame size in milliseconds
BS = int(SF*FS/1000) # Block size in short ints
TIME_TRAVEL = BS * 5 # How long we wait to play back audio we recieve, in nanoseconds
SILENCE_DISTANCE = 10 # The farthest a player can be and still be heard (this is the default, the actual value is loaded from the server)
PEAK_DISTANCE = 3 # How close a player must be to be heard at the maximum volume (this is the default, the actual value is loaded from the server)
VOLUME_SLOPE = 1/(PEAK_DISTANCE - SILENCE_DISTANCE) # Multiplication is faster than division
BUFFER_SIZE = BS * 100 # Audio output buffer size (not latency)

def send(connection, data, address):
    total = connection.sendto(data, address)
    if total < len(data):
        return False
    return True

def receive(connection, expectedAddress):
    data, address = (None, None)
    while address != expectedAddress:
        data, address = connection.recvfrom(Packets.MAX_PACKET_SIZE)
    header = Packets.Header.unpack(data[:Packets.HEADER_LEN])
    packet = Packets.PACKET_TYPE_TABLE[header.ty].unpack(header, data[Packets.HEADER_LEN:header.size + Packets.HEADER_LEN])
    return packet

def clamp(num, lower, upper):
    return max(min(num, upper), lower)

def sliceBufRepeating(idx, sliceLen, buf):
    if sliceLen + idx < len(buf):
        return (buf[idx:(idx + sliceLen), :], np.empty((0, 1)))
    else:
        return (buf[idx:, :], buf[:sliceLen + idx - len(buf), :])
