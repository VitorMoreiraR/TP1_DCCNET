# client.py
import socket
import logging
import hashlib

def config_socket(server_host, port):
    try:
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv6")
    except:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv4")
        
    client.settimeout(0.55)
    return client



