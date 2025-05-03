import hashlib
from .constants import MAX_FRAME_SIZE, FLAG_ACK, FLAG_DATA
from .manipulation_frame import (
    convert_response_to_dictionary,
    create_frame_confirmation,
    create_frame_md5,
    create_data_frame,
)


def make_autentication(gas_in_bytes, client):

    client.send(create_data_frame(gas_in_bytes, FLAG_ACK))  # enviando gas

    response = client.recv(MAX_FRAME_SIZE)  # pegando o ack
    frame = convert_response_to_dictionary(response)  # convertendo para um dicionário

    response = client.recv(MAX_FRAME_SIZE)
    frame = convert_response_to_dictionary(
        response
    )  # recebendo o data "atenticação completa"

    client.send(
        create_frame_confirmation(FLAG_ACK)
    )  # envia a confirmação de recebimento - flag ack

    md5_hash = hashlib.md5(frame["data"][:-1])  # cria o md5 sem o \n

    frame_md5 = create_frame_md5(md5_hash, FLAG_DATA)
    client.send(frame_md5)

    response = client.recv(MAX_FRAME_SIZE)
    frame = convert_response_to_dictionary(response)
