import socket
import logging

from .constants import SOCKET_TIMEOUT, MAX_16BIT, PAD_BYTE


def carry_around_add(a, b):
    c = a + b
    return (c & MAX_16BIT) + (c >> 16)


def internet_checksum(data):
    if len(data) % 2 == 1:
        data += PAD_BYTE
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i + 1] << 8)
        s = carry_around_add(s, w)
    return (~s & MAX_16BIT).to_bytes(2, byteorder="little")


def is_checksum_correct(checksum_frame, frame_without_checksum):
    return checksum_frame == internet_checksum(frame_without_checksum)


def config_socket(server_host, port):
    try:
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv6")
    except:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv4")

    client.settimeout(SOCKET_TIMEOUT)
    return client


def setup_logger():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def parse_ip_port(ip_port):
    if ip_port.startswith("["):
        end = ip_port.find("]")
        if end == -1:
            raise ValueError("Formato invalido")
        ip = ip_port[1:end]
        port_part = ip_port[end + 1 :]
        if port_part.startswith(":"):
            port = int(port_part[1:])
        else:
            raise ValueError("Porta invalida")
        return ip, port
    else:
        parts = ip_port.rsplit(":", 1)
        if len(parts) != 2:
            raise ValueError("Formato invalido")
        ip, port = parts[0], int(parts[1])
        return ip, port
