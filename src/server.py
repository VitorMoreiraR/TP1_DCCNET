import argparse
import asyncio
import socket
import sys
from core.connection import handle_connection_async

async def run_server_async(port, input_path, output_path):
    async def client_handler(reader, writer):
        await handle_connection_async(reader, writer, input_path, output_path)

    server = await asyncio.start_server(
        client_handler, host="", port=port, family=socket.AF_UNSPEC, reuse_address=True
    )

    addr = server.sockets[0].getsockname()
    print(f"Servidor rodando na porta {port} ({addr})")

    async with server:
        await server.serve_forever()


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
    parser = argparse.ArgumentParser(description="DCCNET File Transfer Application")
    parser.add_argument(
        "-s", nargs=3, metavar=("PORT", "INPUT", "OUTPUT"), help="Modo servidor"
    )
    parser.add_argument(
        "-c", nargs=3, metavar=("IP:PORT", "INPUT", "OUTPUT"), help="Modo cliente"
    )

    args = parser.parse_args()

    if args.s:
        port = int(args.s[0])
        asyncio.run(run_server_async(port, args.s[1], args.s[2]))
    elif args.c:
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
