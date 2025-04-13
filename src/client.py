# client.py
import socket
import logging

def config_socket(server_host, port):
    try:
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv6")
    except:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_host, port))
        logging.info("Conectado via IPv4")
    return client

def get_response(data_to_send, client):
    client.settimeout(20)
    try:
        client.send(data_to_send)
        response = client.recv(4096)
    except socket.timeout:
        logging.error("Tempo de resposta esgotado.")
        client.close()
        exit()
    return response
