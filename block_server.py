import asyncio
import json
import subprocess
import threading

from parsedata import parse


class Server:

    def __init__(self):
        file = open('config.json')
        config = json.load(file)
        self.host = config['host']
        self.port = config['port_blocks']
        self.peer_list = {}

    async def listen_and_accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        data = None
        msg = ""
        addr, port = "", ""
        addr, port = writer.get_extra_info("peername")
        self.peer_list[str(addr)+':'+str(port)] = (reader, writer)

    async def run_server(self) -> None:
        #print("Server listen started")
        server = await asyncio.start_server(self.listen_and_accept, self.host, self.port)

        async with server:
            await server.serve_forever()

    async def send_data(self):
        PEER_LIST2 = {}
        with open('nodine.log', "r") as f1:
            while True:
                peer_list2 = self.peer_list.copy()
                last_line = ""
                try:
                    last_line = f1.readlines()[-1:][0]
                    #print(last_line)
                except:
                    continue
                try:
                    data = parse(last_line)
                    if data == "":
                        continue
                except Exception as e:
                    #print("First exception " + str(e))
                    continue

                for el in PEER_LIST2:
                    try:
                        reader, writer = peer_list2[el]
                        addr, port = writer.get_extra_info("peername")
                        if writer.is_closing():
                            raise Exception("Socket closed")
                        #await asyncio.sleep(0.2)
                        writer.write(data.encode())
                        await writer.drain()
                        #print(f'Sending data: {data}')
                    except Exception as e:
                        print("Second exception " + str(e))
                        try:
                            return_query = subprocess.run(["fuser", "-k", str(port) + "/tcp"])
                            reader, writer = peer_list2[el]
                            self.peer_list.pop(el)
                            #print(f'Removing connection: {el}')
                        except Exception as e:
                            print("Third exception " + str(e))
                            continue
        #print("Closed file")

if __name__ == '__main__':
    server = Server()
    _thread = threading.Thread(target=asyncio.run, args=(server.send_data(),))
    _thread.start()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server.run_server())
