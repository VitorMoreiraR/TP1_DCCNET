import argparse
import socket
import sys
import threading
from manipulation_frame import (
    create_data_frame_authentication,
    convert_response_to_dictionary,
    create_frame_confirmation,
)

FLAG_GENERIC_DATA = bytes.fromhex("00")
FLAG_CONFIRMATION = bytes.fromhex("80")
FLAG_END = bytes.fromhex("40")


def send_file(sock, filepath):
    id_data = 0
    with open(filepath, "rb") as f:
        while chunk := f.read(1024):
            frame = create_data_frame_authentication(chunk, id_data)
            sock.sendall(frame)
            id_data ^= 1
        frame = create_data_frame_authentication(b"", id_data, flag=FLAG_END)
        sock.sendall(frame)


def receive_file(sock, output_path):
    with open(output_path, "wb") as f:
        while True:
            frame = sock.recv(4096)
            if not frame:
                break

            info = convert_response_to_dictionary(frame)
            flag = info["flag"]
            data = info["data"]
            frame_id = info["id"]

            if flag == FLAG_GENERIC_DATA:
                f.write(data.encode('ascii'))
                sock.sendall(create_frame_confirmation(frame_id))

            elif flag == FLAG_END:
                print("[INFO] FLAG_END")
                break

    sock.close()
    print("[INFO] Arquivo salvo e conexão encerrada.")


def handle_connection(sock, input_path, output_path):
    t_send = threading.Thread(target=send_file, args=(sock, input_path))
    t_recv = threading.Thread(target=receive_file, args=(sock, output_path))
    t_send.start()
    t_recv.start()
    t_send.join()
    t_recv.join()
    sock.close()


def run_server(port, input_path, output_path):
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("", port))
        server.listen(1)
        print(f"Servidor rodando na porta {port}")
        conn, addr = server.accept()
        print(f"Conexao com {addr}")
        handle_connection(conn, input_path, output_path)


def parse_ip_port(ip_port):
    if ip_port.startswith('['):
        end = ip_port.find(']')
        if end == -1:
            raise ValueError("Formato invalido")
        ip = ip_port[1:end]
        port_part = ip_port[end+1:]
        if port_part.startswith(':'):
            port = int(port_part[1:])
        else:
            raise ValueError("Porta invalida")
        return ip, port
    else:
        parts = ip_port.rsplit(':', 1)
        if len(parts) != 2:
            raise ValueError("Formato invalido")
        ip, port = parts[0], int(parts[1])
        return ip, port


def run_client(ip, port, input_path, output_path):
    try:
        for res in socket.getaddrinfo(ip, port, proto=socket.IPPROTO_TCP):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype)
                sock.connect(sa)
                print(f"Conectado: {sa}")
                handle_connection(sock, input_path, output_path)
                return
            except socket.error as e:
                print(f"Erro ao conectar: {e}")
                continue
        print("Falha ao conectar")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='DCCNET File Transfer Application')
    parser.add_argument('-s', nargs=3, metavar=('PORT', 'INPUT', 'OUTPUT'), help='Modo servidor')
    parser.add_argument('-c', nargs=3, metavar=('IP:PORT', 'INPUT', 'OUTPUT'), help='Modo cliente')

    args = parser.parse_args()

    if args.s:
        port = int(args.s[0])
        run_server(port, args.s[1], args.s[2])
    elif args.c:
        ip_port = args.c[0]
        input_path = args.c[1]
        output_path = args.c[2]
        try:
            ip, port = parse_ip_port(ip_port)
            run_client(ip, port, input_path, output_path)
        except ValueError as e:
            print(f"Error parsing IP:PORT: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()