import asyncio
from .manipulation_frame import (
    convert_response_to_dictionary,
    create_data_frame,
    create_frame_confirmation,
)
from .constants import FLAG_GENERIC_DATA, FLAG_CONFIRMATION, FLAG_END, EMPTY_DATA
from .exceptions import InvalidChecksumError


async def handle_connection_async(reader, writer, input_path, output_path):
    can_send_condition = asyncio.Condition()
    can_stop_condition = asyncio.Condition()
    can_send = False
    sender_done = False
    receiver_done = False

    async def sender():
        nonlocal can_send, sender_done, receiver_done
        id_data = 0
        with open(input_path, "rb") as f:
            while chunk := f.read(1000):
                tentativa = 0
                while tentativa < 16:
                    frame = create_data_frame(chunk, id_data)
                    writer.write(frame)
                    await writer.drain()
                    id_data ^= 1
                    try:
                        async with can_send_condition:
                            while not can_send:
                                await asyncio.wait_for(
                                    can_send_condition.wait(),
                                    timeout=0.6,
                                )
                        break
                    except asyncio.TimeoutError:
                        tentativa = tentativa + 1
                can_send = False
                if receiver_done:
                    frame = await reader.read(4096 + 120)
                    try:
                        info = convert_response_to_dictionary(frame)
                        flag = info["flag"]
                        if flag == FLAG_CONFIRMATION:
                            async with can_send_condition:
                                can_send = True
                    except (InvalidChecksumError) as e:
                             print(f"{type(e).__name__}: {e}")
        frame = create_data_frame(EMPTY_DATA, id_data, flag=FLAG_END)
        writer.write(frame)
        await writer.drain()

        async with can_stop_condition:
            sender_done = True
            can_stop_condition.notify()

    async def receiver():
        nonlocal can_send, receiver_done
        with open(output_path, "wb") as f:
            while True:
                frame = await reader.read(4096 + 120)
                if not frame:
                    break
                try:
                    info = convert_response_to_dictionary(frame)
                    flag = info["flag"]
                    data = info["data"]
                    frame_id = info["id"]

                    if flag == FLAG_CONFIRMATION:
                        async with can_send_condition:
                            can_send = True
                            can_send_condition.notify()

                    if flag == FLAG_GENERIC_DATA or (
                        flag == FLAG_END and data != EMPTY_DATA
                    ):
                        f.write(data)
                        writer.write(create_frame_confirmation(frame_id))
                        await writer.drain()

                    if flag == FLAG_END:
                        async with can_send_condition:
                            can_send = True
                            receiver_done = True
                            can_send_condition.notify()
                        async with can_stop_condition:
                            can_stop_condition.notify()
                        break
                except (InvalidChecksumError) as e:
                             print(f"{type(e).__name__}: {e}")
                             
    await asyncio.gather(asyncio.create_task(sender()), asyncio.create_task(receiver()))

    async with can_stop_condition:
        while not (sender_done and receiver_done):
            await can_stop_condition.wait()

    print("[INFO] Arquivo salvo e conexão encerrada.")
    writer.close()
    await writer.wait_closed()
