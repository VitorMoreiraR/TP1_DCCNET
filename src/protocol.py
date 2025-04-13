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

def create_data_frame_authentication(gas_in_bytes):
    id = 0
    header = SYNC_BYTES + SYNC_BYTES
    length = len(gas_in_bytes).to_bytes(2, byteorder="big")
    identifier = id.to_bytes(2, byteorder="big")
    frame = header + bytes.fromhex('0000') + length + identifier + FLAG_GENERIC_DATA + gas_in_bytes
    checksum = internet_checksum(frame)
    return header + checksum + length + identifier + FLAG_GENERIC_DATA + gas_in_bytes

def parse_dccnet_frames(response):
    md5s = []
    i = 0
    while i <= len(response) - 8:
        if response[i:i+4] == SYNC_BYTES and response[i+4:i+8] == SYNC_BYTES:
            if i + 15 > len(response):
                break  # cabeçalho incompleto

            chksum = response[i+8:i+10]
            length = int.from_bytes(response[i+10:i+12], byteorder='big')
            id_ = response[i+12:i+14]
            flag = response[i+14:i+15]

            total_length = 15 + length
            if i + total_length > len(response):
                break  # frame incompleto

            payload = response[i+15:i+15+length]
            frame = response[i:i+total_length]

            # Zerar campo de checksum antes de calcular
            frame_for_checksum = frame[:8] + b'\x00\x00' + frame[10:]
            calculated_chksum = internet_checksum(frame_for_checksum)

            if calculated_chksum == chksum:
                try:
                    md5 = payload.decode('ascii').strip()
                    md5s.append(md5)
                except:
                    pass  # payload inválido
            else:
                # Checksum inválido — ignora frame
                pass

            i += total_length
        else:
            i += 1
    return md5s
