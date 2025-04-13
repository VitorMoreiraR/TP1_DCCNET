# main.py
import argparse
import logging

from client import config_socket, get_response
from protocol import create_data_frame_authentication, parse_dccnet_frames

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Cliente de envio de G.A.S.")
    parser.add_argument("host_port", help="Servidor no formato HOST:PORTA")
    parser.add_argument("gas", nargs="+", help="Conteúdo G.A.S. para envio")
    return parser.parse_args()

def main():
    setup_logger()
    args = parse_args()

    try:
        server_host, port = args.host_port.split(':')
        gas = ' '.join(args.gas) + '\n'
        gas_in_bytes = gas.encode('ascii')

        client = config_socket(server_host, int(port))
        frame = create_data_frame_authentication(gas_in_bytes)
        logging.info(f"Enviado: {frame}")

        response = get_response(frame, client)
        
        logging.info(f"Recebido: {response}")
        
        md5s = parse_dccnet_frames(response)
        for md5 in md5s:
            print(md5)

    except Exception as e:
        logging.exception("Erro na execução do cliente.")

if __name__ == "__main__":
    main()
