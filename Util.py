import socket

import numpy as np

import Packets

SF = 48000 # Sampling frequency in hertz
FS = 20 # Frame size in milliseconds
BS = int(SF*FS/1000) # Block size in short ints
TIME_TRAVEL = 25 # How long we wait to play back audio we recieve, in milliseconds
SILENCE_DISTANCE = 10 # The farthest a player can be and still be heard (this is the default, the actual value is loaded from the server)
PEAK_DISTANCE = 3 # How close a player must be to be heard at the maximum volume (this is the default, the actual value is loaded from the server)
VOLUME_SLOPE = 1/(Util.PEAK_DISTANCE - Util.SILENCE_DISTANCE) # Multiplication is faster than division
BUFFER_SIZE = BS * 25 # Audio output buffer size (not latency)

def send(connection, data, address):
    total = connection.sendto(data[0], address)
    total += connection.sendto(data[1], address)
    if total < len(data[0]) + len(data[1]):
        return False
    return True

def receive(connection, expectedAddress):
    data, address = (None, None)
    while address != expectedAddress:
        data, address = connection.recvfrom(Packets.HEADER_LEN)
    header = Packets.Header.unpack(data)
    data, address = (None, None)
    while address != expectedAddress:
        data, address = connection.recvfrom(header.size)
    packet = Packets.PACKET_TYPE_TABLE[header.ty].unpack(header, data)
    return packet

def clamp(num, lower, upper):
    return max(min(num, lower), upper)

def timestampToIndex(baseTime, timestamp, sampleRate):
    return sampleRate * int(timestamp - baseTime)

def sliceBufRepeating(idx, sliceLen, buf):
    if sliceLen + idx < len(buf):
        return (buf[idx:sliceLen, :], None)
    else:
        return (buf[idx:], buf[:sliceLen + idx - len(buf), :])
