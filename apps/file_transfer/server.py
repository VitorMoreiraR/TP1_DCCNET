import argparse
import asyncio
import socket
from dccnet.connection import handle_connection_async


async def run_server_async(port, input_path, output_path):
    async def client_handler(reader, writer):
        await handle_connection_async(reader, writer, input_path, output_path)

    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # <- ESSENCIAL para dual-stack
    sock.bind(('::', port))  # Bind em todas interfaces (IPv6 e IPv4)
    sock.listen(100)
    sock.setblocking(False)

    
    server = await asyncio.start_server(
        client_handler, sock=sock#host="", port=port, family=socket.AF_UNSPEC, reuse_address=True
    )

    addr = server.sockets[0].getsockname()
    print(f"Servidor rodando na porta {port} ({addr})")

    async with server:
        await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="DCCNET File Transfer Server")
    parser.add_argument(
        "-s", nargs=3, metavar=("PORT", "INPUT", "OUTPUT"), help="Modo servidor"
    )

    args = parser.parse_args()

    if args.s:
        port = int(args.s[0])
        asyncio.run(run_server_async(port, args.s[1], args.s[2]))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
