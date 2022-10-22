import asyncio
from asyncore import write
import time

host = '127.0.0.1'
PORT = 55555

async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    data = None
    msg = ""
    addr, port = "", ""

    while msg.find("<quit>") == -1 :
        data = await reader.read(4096)
        msg = data.decode()
        writer.write(data)
        await writer.drain()

    writer.close()
    await writer.wait_closed()


async def run_client() -> None:
    reader, writer = await asyncio.open_connection(HOST, PORT)

    await writer.drain()

    while True:
        data = await reader.read(1024)

        if not data:
            raise Exception("socket closed")

        print(f"Recieved: {data.decode()}")


loop = asyncio.new_event_loop()
loop.run_until_complete(run_client())
