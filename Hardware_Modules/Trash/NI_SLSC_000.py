import urllib3
import json
# Define RPC Method Structure
init_request = {"id": "1","jsonrpc": "2.0","method": "initializeSession","params":{"devices": ""}}
close_request = {"id": "2","jsonrpc": "2.0","method": "closeSession","params":{"session_id": ""}}
get_modules_request = {"id": "12","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": "Dev.Modules"}}
# Initialize Parameters
slsc_chassis_name = "SLSC-12001-0310592E"
slsc_url = f'http://{slsc_chassis_name}/nislsc/call'
session_id = ""
http = urllib3.PoolManager()
# Initialize Session
init_request['params']['devices'] = slsc_chassis_name
response = http.request("POST", slsc_url, body=json.dumps(init_request))
data = json.loads(response.data.decode())
if 'error' in data:
    if 'data' in data['error']:
        print(data['error']['data']['nislsc_message'])
    else:
        print(data['error']['message'])
else:
    session_id = data['result']['session_id']
# Get Modules in Chassis
if session_id:
    get_modules_request["params"]["session_id"] = session_id
    get_modules_request["params"]["devices"] = [slsc_chassis_name]
    response = http.request("POST", slsc_url, body=json.dumps(get_modules_request))
    response_dict = json.loads(response.data)
    if 'result' in response_dict:
        if 'value' in response_dict["result"]:
            print(f'Modules:\n{response_dict["result"]["value"]}')
# Close Session
if session_id:
    close_request['params']['session_id'] = session_id
    response = http.request("POST", slsc_url, body=json.dumps(close_request))
