def recv_bytes(sock, byte_num):
    buf = []
    while byte_num > 0:
        info = sock.recv(byte_num)
        byte_num -= len(info)
        buf.append(info)
    return ''.join(buf)


def prefix_to_len(prefix):
    return ord(prefix[0]) << 24 | \
           ord(prefix[1]) << 16 | \
           ord(prefix[2]) << 8 | \
           ord(prefix[3])


def len_to_prefix(length):
    parts = "".join([
        chr(length >> 24 & 0xff),
        chr(length >> 16 & 0xff),
        chr(length >> 8 & 0xff),
        chr(length & 0xff)])
    return parts
