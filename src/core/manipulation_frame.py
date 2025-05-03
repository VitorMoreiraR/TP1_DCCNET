SYNC_BYTES = bytes.fromhex("DCC023C2")
FLAG_GENERIC_DATA = bytes.fromhex("00")
FLAG_CONFIRMATION = bytes.fromhex("80")
from .protocol import internet_checksum


def is_checksum_correct(checksum_frame, frame_without_checksum):
    return checksum_frame == internet_checksum(frame_without_checksum)


def convert_response_to_dictionary(response):
    count_sync = 0
    i = 0
    checksum = None
    length = None
    id = None
    flag = None
    data = None

    while i < len(response):

        if response[i : i + 4] == SYNC_BYTES and count_sync < 2:
            count_sync = count_sync + 1
            i = i + 4
            continue
        elif count_sync < 2:
            i = i + 1
            continue

        if checksum == None:
            checksum = response[i : i + 2]
            i = i + 2
            continue

        if length == None:
            length = response[i : i + 2]
            i = i + 2
            continue

        if id == None:
            id = response[i : i + 2]
            i = i + 2
            continue

        if flag == None:
            flag = response[i : i + 1]
            i = i + 1
            continue

        if data == None:
            data = response[i : i + int.from_bytes(length)]
            i = i + int.from_bytes(length)
            break
    
    if data is None: data = b''
    
    frame_without_checksum = (
        SYNC_BYTES + SYNC_BYTES + bytes.fromhex("0000") + length + id + flag
    )
    if data:
        frame_without_checksum = frame_without_checksum + data

    if is_checksum_correct(checksum, frame_without_checksum) == False:
        print("----------------------CHECKSUM ERRADO ---------------------------------")

    print(
        f'RESPONSE -> SYNC_BYTES: {SYNC_BYTES.hex()} - SYNC_BYTES: {SYNC_BYTES.hex()} -  checksum: {checksum.hex()} - length: {int.from_bytes(length)} - id: {int.from_bytes(id)} - flag: {flag.hex()} - data: {(data[:2] if data != None else "")}\n'
    )

    return {
        "flag": flag,
        "data": data if data != None else "",
        "id": int.from_bytes(id),
    }


def create_frame_confirmation(id):
    header = SYNC_BYTES + SYNC_BYTES
    identifier = id.to_bytes(2, byteorder="big")
    frame = (
        header
        + bytes.fromhex("0000")
        + bytes.fromhex("0000")
        + identifier
        + FLAG_CONFIRMATION
    )
    checksum = internet_checksum(frame)
    frame = header + checksum + bytes.fromhex("0000") + identifier + FLAG_CONFIRMATION

    print(
        f"SEND -> header: {header} - identifier: {id} - checksum: {checksum.hex()} - flag: {FLAG_CONFIRMATION.hex()}\n"
    )

    return frame


def create_frame_md5(md5_hash, id):

    header = SYNC_BYTES + SYNC_BYTES
    identifier = id.to_bytes(2, byteorder="big")
    payload = md5_hash.hexdigest() + "\n"
    payload = payload.encode("ascii")
    length = len(payload).to_bytes(2, byteorder="big")

    flag = FLAG_GENERIC_DATA

    frame = header + bytes.fromhex("0000") + length + identifier + flag + payload

    checksum = internet_checksum(frame)

    frame = header + checksum + length + identifier + flag + payload

    print(
        f"SEND -> header: {header.hex()} - checksum: {checksum.hex()} - length: {int.from_bytes(length)} - identifier: {id} - flag: {flag.hex()} - payload: {payload}\n"
    )

    return frame


def create_data_frame(data, id, flag=FLAG_GENERIC_DATA):
    header = SYNC_BYTES + SYNC_BYTES
    length = len(data).to_bytes(2, byteorder="big")
    identifier = id.to_bytes(2, byteorder="big")
    frame = header + bytes.fromhex("0000") + length + identifier + flag + data
    checksum = internet_checksum(frame)
    print(
        f"SEND -> header: {header.hex()} - checksum: {checksum.hex()} - length: {int.from_bytes(length)} - identifier: {identifier.hex()} flag: {flag.hex()} - data: {data[:2]}\n"
    )
    return header + checksum + length + identifier + flag + data
