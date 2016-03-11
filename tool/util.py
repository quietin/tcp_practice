import struct


def recv_bytes(sock, byte_num):
    buf = []
    while byte_num > 0:
        info = sock.recv(byte_num)
        byte_num -= len(info)
        buf.append(info)
    return ''.join(buf)


def len_unpack(prefix):
    """network big-endian to int len"""
    return struct.unpack("!I", prefix)[0]


def len_pack(length):
    """int len to network big-endian"""
    return struct.pack("!I", length)
