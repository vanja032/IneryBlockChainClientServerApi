import asyncio
import json
from parsedata import parse
import subprocess
import re
import time

class SERVER:

    def __init__(self):
        
        file = open('config.json')
        config = json.load(file)
        self.HOST = config['host']
        self.PORT = config['port_api']
        self.SERVER_QUEUE_SIZE = config['server_queue_size']
        self.TOKENS = []
        self.Tokens_last_time = time.time()

    async def LISTEN_AND_RETURN(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            data = await reader.read(self.SERVER_QUEUE_SIZE)
            msg = data.decode()
            recv = json.loads(msg)
            action = recv['method']
            #client_id = recv['client_id']
            #event = recv['event_name']
            return_data = ""

            if action == 'get_actions':
                account_name = recv['value']
                pos = recv['pos']
                offset = recv['offset']
                return_query = subprocess.Popen(["cline", "get", "actions", account_name, pos, offset, "--full", "--server", "-j"], stdout=subprocess.PIPE)
                return_text = return_query.communicate()[0]
                return_data = return_text.decode()
                return_data = json.loads(return_data)
                #return_data["client_id"] = client_id
                #return_data["event_name"] = event
                return_data = json.dumps(return_data)
                #print("Call API " + action)
                return_data = return_data + "<end>"
                writer.write(return_data.encode())
                await writer.drain()

            if action == 'get_schedule':
                return_query = subprocess.Popen(["cline", "get", "schedule", "-j"], stdout=subprocess.PIPE)
                return_text = return_query.communicate()[0]
                return_data = return_text.decode()
                #print("Call API " + action)
                return_data = return_data + "<end>"
                writer.write(return_data.encode())
                await writer.drain()

                

            if action == 'get_tokens':
                if not self.TOKENS or time.time() > self.Tokens_last_time + 60:
                    get_tokens = subprocess.Popen(["cline", "get", "currency", "balance", "inery.token", "inery"], stdout=subprocess.PIPE)
                    out = get_tokens.communicate()[0]
                    outp = out.decode().split("\n")
                    outp = outp[:-1]
                    tokens = []
                    for curr in outp:
                        re.sub(' +', ' ', curr)
                        curr_tokens = curr.split(" ")
                        curr_token = curr_tokens[1]
                        get_token_acc = subprocess.Popen(["cline", "get", "currency", "stats", "inery.token", curr_token], stdout=subprocess.PIPE)
                        out2 = get_token_acc.communicate()[0]
                        out2d = out2.decode()
                        acc = json.loads(out2d)[curr_token]["issuer"]
                        token_data = '{"token_name":"' + curr_token + '", "account_name":"' + acc + '"}' + "<end>"
                        writer.write(token_data.encode())
                        await writer.drain()
                        tokens.append({"token_name":curr_token, "account_name":acc})
                
                    self.TOKENS = tokens
                    self.Tokens_last_time = time.time()
                   
                else:
                    rtrn_data = self.TOKENS.copy()
                    for data in rtrn_data:
                        token_data = json.dumps(data) + "<end>"
                        writer.write(token_data.encode())
                        await writer.drain()


            writer.close()
            await writer.wait_closed()
        except:
            writer.close()
            await writer.wait_closed()


    async def RUN_SERVER(self) -> None:
        server = await asyncio.start_server(self.LISTEN_AND_RETURN, self.HOST, self.PORT)
        async with server:
            await server.serve_forever()
                
if __name__ == '__main__':
    server = SERVER()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server.RUN_SERVER())
