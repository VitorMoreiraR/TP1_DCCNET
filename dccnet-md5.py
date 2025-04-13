import socket
import ipaddress
import argparse
import os
import sys

SYNC_BYTES =  bytes.fromhex('DCC023C2')
FLAG_GENERIC_DATA = bytes.fromhex('00')

 
def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)
#peguei do stack e o gtp traduziu para bits
def internet_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8)
        s = carry_around_add(s, w)

    return (~s & 0xffff).to_bytes(2, byteorder="little")
    
    

def create_data_frame_autentication(gas_in_bytes):
    id = 0
    chksum = internet_checksum(SYNC_BYTES + SYNC_BYTES + bytes.fromhex('0000') + len(gas_in_bytes).to_bytes(2, byteorder="big") + id.to_bytes(2, byteorder="big") + FLAG_GENERIC_DATA + gas_in_bytes)
    return  SYNC_BYTES + SYNC_BYTES + chksum + len(gas_in_bytes).to_bytes(2, byteorder="big") + id.to_bytes(2, byteorder="big") + FLAG_GENERIC_DATA + gas_in_bytes

def config_socket(server_host, port):
    client = None
    try: 
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #ipv6 e UDP
        client.connect((server_host, port))
    except:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 e UDP
        client.connect((server_host, port))
    return client

def get_response(data_to_send, client):
    client.settimeout(20)
    try:
        client.send(data_to_send)
        response = client.recv(4096)
    except socket.timeout:
        client.close()
        exit()
    return response

def get_gas(argv):
    gas = ''
    for index, part_of_gas in enumerate(argv):
        gas = gas + part_of_gas

        if index < len(argv) - 1:
            gas = gas + ' '
        else: 
            gas = gas + '\n'
    return gas
        

def main(argv):
    server_host, port = argv[0].split(':')
    gas = get_gas(argv[1:])
    gas_in_bytes = bytes(gas, encoding="ASCII")
    client = config_socket(str(server_host), int(port))
    frame_autentication = create_data_frame_autentication(gas_in_bytes)
    response = get_response(frame_autentication, client)
    print(response)
    

    
#2022036012  :1:acc52bf6d9303c4e0862712a6a1142d4ccbeaece39f564352fd758e75271362a+2022036012  :2:9c05f9346cfff41fb2e168dd4a9c0e854174010e9d06b63721bcd7b7a857bdf8+2022036012  :3:2cbf8ae806ab2526d0b8675a98dde6dd4318a19709d193ffdd5199b362e5004f+629c8e6c8b6122b421dcd43be0edce0d6e334da5a0c7989a0037d394cfe4ef23
if __name__ == "__main__":
    main(sys.argv[1:])