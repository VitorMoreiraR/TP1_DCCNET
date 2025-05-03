import argparse

from dccnet.autentication import make_autentication
from dccnet.comunication import make_comunication
from dccnet.utils import setup_logger, config_socket


def parse_args():
    parser = argparse.ArgumentParser(description="Cliente de envio de G.A.S.")
    parser.add_argument("host_port", help="Servidor no formato HOST:PORTA")
    parser.add_argument("gas", help="Conteúdo G.A.S. para envio")
    return parser.parse_args()


def main():
    setup_logger()
    args = parse_args()

    server_host, port = args.host_port.split(":")
    gas = args.gas + "\n"
    gas_in_bytes = gas.encode("ascii")

    client = config_socket(server_host, int(port))

    make_autentication(gas_in_bytes, client)
    make_comunication(client)


if __name__ == "__main__":
    main()
