import socket

import Packets

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
