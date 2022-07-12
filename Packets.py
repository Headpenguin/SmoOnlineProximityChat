from struct import *
from enum import *
import uuid

HEADER_FORMAT = '<2h'
INIT_FORMAT = '<2fI'
VOICE_FORMAT = '<If'

HEADER_LEN = 20
INIT_LEN = calcsize(INIT_FORMAT)
MAX_PACKET_SIZE = 2840 + 8 + HEADER_LEN

class ZeroIndex(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
         return count

class PacketTypes(ZeroIndex):
    Unknown = auto()
    Init = auto()
    Player = auto()
    Cap = auto()
    Game = auto()
    Tag = auto()
    Connect = auto()
    Disconnect = auto()
    Costume = auto()
    Shine = auto()
    Capture = auto()
    ChangeStage = auto()
    ChatConnect = auto()
    ChatInit = auto()
    ChatVoice = auto()
    Command = auto()



class Header:
    def __init__(self, GUID, ty, size):
        self.GUID, self.ty, self.size = (GUID, ty, size)
        #print(self.size)
        
    @classmethod
    def unpack(cls, msg):
        ty, size = unpack(HEADER_FORMAT, msg[16:])
        GUID = uuid.UUID(bytes_le=msg[:16])
        return cls(GUID, ty, size)

#    def unpackInPlace(self, msg):
#       ty, size = unpack(HEADER_FORMAT, msg[16:])
#       GUID = uuid.UUID(bytes_le=msg[:16])
#       return self.__init__(GUID, ty, size)

    def pack(self):
        return  self.GUID.bytes_le + pack(HEADER_FORMAT, self.ty, self.size)

class Packet:
    ClientGUID = uuid.UUID(bytes=b'\x00'*16)
    def __init__(self, header):
        self.reinit(header)

    def reinit(self, header):
        self.header = header

    @classmethod
    def unpack(cls, header, msg):
        return cls(header)

    def pack(self):
        return self.header.pack()

class Connect(Packet):
    def __init__(self, name):
        Packet.__init__(self, Header(Packet.ClientGUID, PacketTypes.ChatConnect, len(name.encode())))
        self.name = name
        
    @classmethod
    def unpack(cls, header, msg):
        obj = cls(msg.decode())
        obj.header = header
        return obj

    def pack(self):
        return Packet.pack(self) + self.name.encode()

class Init(Packet):
    def __init__(self, silenceDistance, peakDistance, currentFrame):
        Packet.__init__(self, Header(Packet.ClientGUID, PacketTypes.ChatInit, 12))
        self.silenceDistance = silenceDistance
        self.peakDistance = peakDistance
        self.currentFrame = currentFrame

    @classmethod
    def unpack(cls, header, msg):
        silenceDistance, peakDistance, currentFrame = unpack(INIT_FORMAT, msg)
        obj = cls(silenceDistance, peakDistance, currentFrame)
        obj.header = header
        return obj

    def pack(self):
        return Packet.pack(self) + pack(INIT_FORMAT, self.silenceDistance, self.peakDistance, currentFrame)

    def setGUID(self):
        Packet.ClientGUID = self.header.GUID

class Voice(Packet):
    def __init__(self, time, buf):
        self.reinit(time, buf)

    def reinit(self, currentFrame, buf):
        Packet.reinit(self, Header(Packet.ClientGUID, PacketTypes.ChatVoice, len(buf) + 8))
        #print(len(buf))
        self.currentFrame = currentFrame
        self.buf = buf
        self.distance = 0
        
    @classmethod
    def unpack(cls, header, msg):
        #print(header.size)
        currentFrame, distance = unpack(VOICE_FORMAT, msg[:8])
        obj = cls(currentFrame, msg[8:])
        obj.header = header
        obj.distance = distance
        #print(obj.buf)
        return obj

    def pack(self):
        return Packet.pack(self) + pack(VOICE_FORMAT, self.currentFrame, self.distance) + self.buf

    def getDistance(self):
        return self.distance

    def decode_float(self, decoder, frameSize):
        return decoder.decode_float(self.buf, frameSize)

    def getFrame(self):
        return self.currentFrame

PACKET_TYPE_TABLE = {
    PacketTypes.Unknown: Packet,
    PacketTypes.ChatConnect: Connect,
    PacketTypes.ChatInit: Init,
    PacketTypes.ChatVoice: Voice
}        
        
        
