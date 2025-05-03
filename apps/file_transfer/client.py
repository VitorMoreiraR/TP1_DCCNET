import argparse
import asyncio
import socket
import sys
from dccnet.connection import handle_connection_async
from dccnet.utils import parse_ip_port


async def run_client(ip, port, input_path, output_path):
    try:
        reader, writer = await asyncio.open_connection(
            ip, port, family=socket.AF_UNSPEC
        )

        print(f"Conectado a {ip}:{port}")

        await handle_connection_async(reader, writer, input_path, output_path)

    except Exception as e:
        reader, writer = await asyncio.open_connection(ip, port, family=socket.AF_INET)

        print(f"Conectado a {ip}:{port}")

        await handle_connection_async(reader, writer, input_path, output_path)


def main():
    parser = argparse.ArgumentParser(description="DCCNET File Transfer Client")
    parser.add_argument(
        "-c", nargs=3, metavar=("IP:PORT", "INPUT", "OUTPUT"), help="Modo cliente"
    )

    args = parser.parse_args()

    if args.c:
        ip_port = args.c[0]
        input_path = args.c[1]
        output_path = args.c[2]
        try:
            ip, port = parse_ip_port(ip_port)
            asyncio.run(run_client(ip, port, input_path, output_path))
        except ValueError as e:
            print(f"Error parsing IP:PORT: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
