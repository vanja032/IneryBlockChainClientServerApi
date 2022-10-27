import subprocess
import json

def parse(data):
    data = str(data)
    parsed_data = {}
    send_data = ""
    try:
        if (data.find("on_incoming_block") != -1 and data.find("Received block") != -1) or (data.find("produce_block") != -1 and data.find("Produced block") != -1):
            datap = data.split("]")[1].lstrip().split(" ")
            parsed_data["block_address"] = datap[2]
            parsed_data["block_num"] = datap[3]
            parsed_data["creation_time"] = datap[5]
            parsed_data["signed"] = datap[8]
            get_account_info = subprocess.Popen(["cline", "get", "account", parsed_data["signed"], "-j"], stdout=subprocess.PIPE)
            out = get_account_info.communicate()[0]
            outd = json.loads(out.decode())
            parsed_data["account_created"] = outd["created"]
            parsed_data["transaction"] = datap[10].replace(",", "")
            if parsed_data["transaction"] != "0":
                return_query = subprocess.Popen(["cline", "get", "block", parsed_data["block_num"][1:]], stdout=subprocess.PIPE)
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
            send_data = str(parsed_data)+"<end>"
    except Exception as e:
        #print("C" + str(e))
        return send_data
    return send_data


#parse("Recieved: 'info  2022-09-30T13:51:28.303 nodine    producer_plugin.cpp:404       on_incoming_block    ] Received block 70fd8150b3f59e48... #1528139 @ 2022-09-30T13:51:28.500 signed by prod2 [trxs: 0, lib: 152813")
