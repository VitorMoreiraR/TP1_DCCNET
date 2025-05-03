import hashlib
from .constants import (
    FLAG_CONFIRMATION,
    FLAG_END,
    FLAG_GENERIC_DATA,
    MESSAGE_END,
    EMPTY_DATA,
)
from .manipulation_frame import (
    convert_response_to_dictionary,
    create_frame_confirmation,
    create_frame_md5,
)


def make_comunication(client):

    mensage = EMPTY_DATA
    id_ask = 1
    id_data = 0
    a = 0
    frame_md5 = EMPTY_DATA
    ack_expected = False
    while True:
        try:
            response = client.recv(4096 + 120)
            frame = convert_response_to_dictionary(response)

            if frame["flag"] != FLAG_CONFIRMATION and ack_expected == True:
                raise Exception("ACK NÂO RETORNADO")

            if frame["flag"] == FLAG_CONFIRMATION and mensage.endswith(MESSAGE_END):
                mensage = EMPTY_DATA
                ack_expected = False

            if frame["flag"] == FLAG_GENERIC_DATA or frame["flag"] == FLAG_END:
                mensage += frame["data"]
                client.send(create_frame_confirmation(id_ask))
                id_ask = 0 if id_ask == 1 else 1

            if frame["flag"] == FLAG_GENERIC_DATA and mensage.endswith(MESSAGE_END):
                md5_hash = hashlib.md5(mensage[:-1])
                frame_md5 = create_frame_md5(md5_hash, id_data)
                client.send(frame_md5)
                id_data = 0 if id_data == 1 else 1
                ack_expected = True

            if frame["flag"] == FLAG_END:
                break

        except:
            if frame["flag"] == FLAG_GENERIC_DATA and mensage.endswith(MESSAGE_END):
                client.send(frame_md5)
                print("RETRASMITION\n")  # ocorre quando não recebo o ask do servidor
