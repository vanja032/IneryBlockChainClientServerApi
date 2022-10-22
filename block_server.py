import asyncio
import threading
import json
from parsedata import parse
import subprocess

class SERVER:

    def __init__(self):
        
        file = open('config.json')
        config = json.load(file)
        self.HOST = config['host']
        self.PORT = config['port']
        self.PEER_LIST = {}

    async def LISTEN_AND_ACCEPT(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        data = None
        msg = ""
        addr, port = "", ""
        #PEER_LIST2 = {}
        
        addr, port = writer.get_extra_info("peername")
        self.PEER_LIST[str(addr)+':'+str(port)] = (reader, writer)

        #PEER_LIST2 = self.PEER_LIST.copy()
        #for el in PEER_LIST2:
        #    print(el)

    async def RUN_SERVER(self) -> None:
        #print("Server listen started")
        server = await asyncio.start_server(self.LISTEN_AND_ACCEPT, self.HOST, self.PORT)
        
        async with server:
            await server.serve_forever()

    async def SEND_DATA(self):
        PEER_LIST2 = {}
        with open('nodine.log', "r") as f1:
            while True:
                PEER_LIST2 = self.PEER_LIST.copy()
                last_line = ""
                try:
                    last_line = f1.readlines()[-1]
                except:
                    continue
                data = parse(last_line)
                if data == "":
                    continue
                for el in PEER_LIST2:
                    try:
                        reader, writer = PEER_LIST2[el]
                        addr, port = writer.get_extra_info("peername")
                        if writer.is_closing():
                            raise Exception("Socket closed")
                        #await asyncio.sleep(0.2)
                        writer.write(data.encode())
                        await writer.drain()
                        #print(f'Sending data: {data}')
                    except Exception as e:
                        #print("A" + str(e))
                        try:
                            return_query = subprocess.run(["fuser", "-k", str(port) + "/tcp"])
                            reader, writer = PEER_LIST2[el]
                            self.PEER_LIST.pop(el)
                            #print(f'Removing connection: {el}')
                        except Exception as e:
                            #print("B" + str(e))
                            continue
        #print("Closed file")
                
if __name__ == '__main__':
    server = SERVER()
    _thread = threading.Thread(target=asyncio.run, args=(server.SEND_DATA(),))
    _thread.start()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server.RUN_SERVER())
