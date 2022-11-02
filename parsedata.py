import json
import subprocess
import time

sent_blocks = []
max_blocks = 20
lines = ""

def parse(data):
    global sent_blocks
    global max_blocks
    global lines
    parsed_data = {}
    send_data = ""
    try:
        if not ((data.find("on_incoming_block") != -1 and data.find("Received block") != -1) or (data.find("produce_block") != -1 and data.find("Produced block") != -1) or data.find("ms]") != -1):
            lines = ""
            raise Exception("Continue")
        lines = lines + data
        if lines.find("ms]") != -1:
            line = lines[0:lines.find("ms]")]
            lines = lines[lines.find("ms]"):]
            if (line.find("on_incoming_block") != -1 and line.find("Received block") != -1) or (line.find("produce_block") != -1 and line.find("Produced block") != -1):
                datap = line.split("]")[1].lstrip().split(" ")
                if datap.index("block") == -1:
                    raise Exception("Error parsing the data")
                if len(sent_blocks) > max_blocks:
                    sent_blocks.pop(0)
                parsed_data["block_address"] = datap[datap.index("block") + 1]
                parsed_data["block_num"] = datap[datap.index("block") + 2]
                if parsed_data["block_num"] in sent_blocks:
                    raise Exception("Block already exist")
                sent_blocks.append(parsed_data["block_num"])
                parsed_data["creation_time"] = datap[datap.index("block") + 4]
                parsed_data["signed"] = datap[datap.index("block") + 7]
                get_account_info = subprocess.Popen(["cline", "get", "account", parsed_data["signed"], "-j"], stdout=subprocess.PIPE)
                out = get_account_info.communicate()[0]
                outd = json.loads(out.decode())
                parsed_data["account_created"] = outd["created"]
                parsed_data["transaction"] = datap[datap.index("block") + 9].replace(",", "")
                if parsed_data["transaction"] != "0":
                    try:
                        return_query = subprocess.Popen(["cline", "get", "block", parsed_data["block_num"][1:]], stdout=subprocess.PIPE)
                        #time.sleep(0.1)
                        return_text = return_query.communicate()[0]
                        return_data = return_text.decode()
                        return_data = json.loads(return_data)
                        transactions = []
                        for trx in return_data["transactions"]:
                            actions = []
                            for act in trx["trx"]["transaction"]["actions"]:
                                actions.append({"account":act["account"], "action":act["name"], "info":act["data"]})
                            transactions.append({"id":trx["trx"]["id"], "actions":actions})
                        parsed_data["transaction_data"] = transactions
                    except:
                        parsed_data["transaction"] = "0"
                send_data = send_data + str(parsed_data) + "<end>"
    except Exception as e:
        #print("Parse exception " + str(e))
        raise Exception("Parse error " + str(e))
    return send_data
