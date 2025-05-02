import argparse
import socket
import sys
import asyncio

from manipulation_frame import (
    convert_response_to_dictionary,
    create_data_frame,
    create_frame_confirmation
)

FLAG_GENERIC_DATA = bytes.fromhex("00")
FLAG_CONFIRMATION = bytes.fromhex("80")
FLAG_END = bytes.fromhex("40")


import asyncio

async def handle_connection_async(reader, writer, input_path, output_path):
    can_send_condition = asyncio.Condition()
    can_stop_condition = asyncio.Condition()
    can_send = False 
    sender_done = False
    receiver_done = False
    
    async def sender(input_path):
        nonlocal can_send, sender_done
        id_data = 0
        with open(input_path, "rb") as f:
           
            while chunk := f.read(4096):
            
                frame = create_data_frame(chunk, id_data)
                writer.write(frame)
                await writer.drain()
                id_data ^= 1
                async with can_send_condition:
                      while not can_send:
                        await can_send_condition.wait()
                can_send = False
                if(receiver_done):
                    frame = await reader.read(4096 + 120)
                
                    info = convert_response_to_dictionary(frame)
                    flag = info["flag"]
                    
                    if flag == FLAG_CONFIRMATION:
                        async with can_send_condition:
                            can_send = True
                            can_send_condition.notify()
            frame = create_data_frame(b"", id_data, flag=FLAG_END)
            writer.write(frame)
            await writer.drain()
            
            async with can_stop_condition:
                sender_done = True
                can_stop_condition.notify()
        
    async def receiver(output_path):
        
        nonlocal can_send, receiver_done
        
        with open(output_path, "wb") as f:
            while True:
                frame = await reader.read(4096 + 120)
                if not frame:
                    break
               
                info = convert_response_to_dictionary(frame)
                flag = info["flag"]
                data = info["data"]
                frame_id = info["id"]
                
                if flag == FLAG_CONFIRMATION:
                    async with can_send_condition:
                        can_send = True
                        can_send_condition.notify()

                if flag == FLAG_GENERIC_DATA or (flag == FLAG_END and data != ''):
                    f.write(data)
                    writer.write(create_frame_confirmation(frame_id))
                    await writer.drain()

                if flag == FLAG_END:
                    print("[INFO] FLAG_END")
                    async with can_send_condition:
                        can_send = True
                        receiver_done = True
                        can_send_condition.notify()
                    async with can_stop_condition:
                        can_stop_condition.notify()
                    break
                            

         

    send_task = asyncio.create_task(sender(input_path))
    recv_task = asyncio.create_task(receiver(output_path))
    
    await asyncio.gather(send_task, recv_task)
    
    async with can_stop_condition:
        while not (sender_done and receiver_done):
            await can_stop_condition.wait()

    print("[INFO] Arquivo salvo e conexão encerrada.")    
    writer.close()
    await writer.wait_closed()

async def run_server_async(port, input_path, output_path):
    async def client_handler(reader, writer):
        await handle_connection_async(reader, writer, input_path, output_path)

    server = await asyncio.start_server(
        client_handler, host='', port=port, family=socket.AF_UNSPEC, reuse_address=True
    )
    
    addr = server.sockets[0].getsockname()
    print(f"Servidor rodando na porta {port} ({addr})")
    
    async with server:
        await server.serve_forever()

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


async def run_client(ip, port, input_path, output_path):
    try:
        reader, writer = await asyncio.open_connection(ip, port, family=socket.AF_UNSPEC)

        print(f"Conectado a {ip}:{port}")
        
        await handle_connection_async(reader, writer, input_path, output_path)

    except Exception as e:
        reader, writer = await asyncio.open_connection(ip, port, family=socket.AF_INET)

        print(f"Conectado a {ip}:{port}")
        
        await handle_connection_async(reader, writer, input_path, output_path)


def main():
    parser = argparse.ArgumentParser(description='DCCNET File Transfer Application')
    parser.add_argument('-s', nargs=3, metavar=('PORT', 'INPUT', 'OUTPUT'), help='Modo servidor')
    parser.add_argument('-c', nargs=3, metavar=('IP:PORT', 'INPUT', 'OUTPUT'), help='Modo cliente')

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