SYNC_BYTES = bytes.fromhex('DCC023C2')
FLAG_GENERIC_DATA = bytes.fromhex('00')

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def internet_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8)
        s = carry_around_add(s, w)
    return (~s & 0xffff).to_bytes(2, byteorder="little")