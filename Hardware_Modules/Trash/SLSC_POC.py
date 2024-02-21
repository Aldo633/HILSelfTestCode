import urllib3
import json

#Line Direction
Input_Source = 0
Input_Sink = 1
Output_Source = 2
Output_Sink = 3

# Define RPC Method Structure
init_request = {"id": "1","jsonrpc": "2.0","method": "initializeSession","params":{"devices": ""}}
close_request = {"id": "2","jsonrpc": "2.0","method": "closeSession","params":{"session_id": ""}}
get_modules_request = {"id": "12","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": "Dev.Modules"}}
get_DevicePropertyList_request = {"id": "13","jsonrpc": "2.0","method": "getDevicePropertyList","params":{"session_id": "","device":""}}
get_DeviceCommandList_request = {"id": "14","jsonrpc": "2.0","method": "getCommandList","params":{"session_id": "","device":""}}
execute_reserveDevices_request = {"id": "16","jsonrpc": "2.0","method": "reserveDevices","params":{"session_id": "","devices":[""],"access":"ReadWrite","reservation_group":"self_test"}}
execute_unreserveDevices_request = {"id": "16","jsonrpc": "2.0","method": "unreserveDevices","params":{"session_id": "","devices":[""]}}


get_property_request = {"id": "20","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": ""}}
set_property_request =  {"id": "21","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","devices":[""],"physical_channels":[""],"property": "","value":None}}
set_property_commit_request = {"id": "22","jsonrpc": "2.0","method": "commitProperties","params":{"session_id": "","devices":[""],"physical_channels":[""]}}

# Initialize Parameters
slsc_chassis_name = "SLSC-12001-0310592E"
slsc_module_name = ""
slsc_url = f'http://{slsc_chassis_name}/nislsc/call'
session_id = ""
http = urllib3.PoolManager()

SLSC_Devices=[]
SLSC_12202_Devices=[]

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
            i=0
            #SLSC_Devices=response_dict["result"]["value"]
            SLSC_Devices.extend(response_dict["result"]["value"])
            #Get list of SLSC-12202 Modules
            for i in range(len(SLSC_Devices)):
                get_property_request["params"]["session_id"] = session_id
                get_property_request["params"]["devices"] = [SLSC_Devices[i]]
                get_property_request["params"]["property"] = "Dev.ProductName"
                response = http.request("POST", slsc_url, body=json.dumps(get_property_request))
                response_dict = json.loads(response.data)
                device_ProductName = str(response_dict["result"]["value"])
                if device_ProductName.find('12202')!=-1:
                      SLSC_12202_Devices.append(SLSC_Devices[i])
            print(f'NB Modules NI SLSC-12202 found in setup: {len(SLSC_12202_Devices)}.')

if len(SLSC_12202_Devices)>0:
    #Reserve Devices
    execute_reserveDevices_request["params"]["session_id"] = session_id
    #execute_reserveDevices_request["params"]["devices"] =['SLSC-12001-0310592E-Mod5']
    #execute_reserveDevices_request["params"]["devices"] = SLSC_Devices
    execute_reserveDevices_request["params"]["devices"] = SLSC_12202_Devices

    response = http.request("POST", slsc_url, body=json.dumps(execute_reserveDevices_request))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        print(f'Error while reserving module: code: {response_dict["error"]["code"]}, Message: {response_dict["error"]["message"]}.')

    # Get Properties and Commands supported by SLSC-12202
    #----- Get Properties supported
    get_DevicePropertyList_request["params"]["session_id"] = session_id
    #get_DevicePropertyList_request["params"]["device"] = SLSC_Devices[0]
    get_DevicePropertyList_request["params"]["device"] = SLSC_12202_Devices[0]

    response = http.request("POST", slsc_url, body=json.dumps(get_DevicePropertyList_request))
    response_dict = json.loads(response.data)

    if 'result' in response_dict:
        if 'static_properties' in response_dict["result"]:
            print(f'Properties supported by SLSC-12202:\n{response_dict["result"]["static_properties"]}')

    #----- Get Commands supported
    get_DeviceCommandList_request["params"]["session_id"] = session_id
    #get_DeviceCommandList_request["params"]["device"] = SLSC_Devices[0]
    get_DeviceCommandList_request["params"]["device"] = SLSC_12202_Devices[0]

    response = http.request("POST", slsc_url, body=json.dumps(get_DeviceCommandList_request))
    response_dict = json.loads(response.data)

    if 'result' in response_dict:
        if 'commands' in response_dict["result"]:
            print(f'Commands supported by SLSC-12202:\n{response_dict["result"]["commands"]}')

    #For all SLSC-12202 Modules: set Ports 0 and 2 as Output, set Ports 1 and 3 as Input
    i=0
    set_property_request["params"]["session_id"] = session_id
    set_property_request["params"]["property"] = "NI.Line.Direction"
    for i in range(len(SLSC_12202_Devices)): 

        #---------- "/port0/line0:7" ---------- 
        set_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port0/line0:7"]
        set_property_request["params"]["value"]=[Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for "/port0/line0:7" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        #---------- "/port1/line0:7" ---------- 
        set_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port1/line0:7"]
        set_property_request["params"]["value"]=[Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for "/port1/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        #---------- "/port2/line0:7" ---------- 
        set_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port2/line0:7"]
        set_property_request["params"]["value"]=[Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for "/port2/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        #---------- "/port3/line0:7" ---------- 
        set_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port3/line0:7"]
        set_property_request["params"]["value"]=[Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for"/port3/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')

    #Commit
    set_property_commit_request["params"]["session_id"] = session_id
    set_property_commit_request ["params"]["devices"] = SLSC_12202_Devices

    response = http.request("POST", slsc_url, body=json.dumps(set_property_commit_request))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        if 'code' in response_dict["error"]:
            print(f'{SLSC_12202_Devices[i]}: error while applying Device Configuration: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')


    # Unreserve Devices
    execute_unreserveDevices_request['params']['session_id'] = session_id
    #execute_unreserveDevices_request["params"]["devices"] = SLSC_Devices
    execute_unreserveDevices_request["params"]["devices"] = SLSC_12202_Devices

    response = http.request("POST", slsc_url, body=json.dumps(execute_unreserveDevices_request))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        print(f'Error while unreserving module: code: {response_dict["error"]["code"]}, Message: {response_dict["error"]["message"]}.')

# Close Session
if session_id:
    close_request['params']['session_id'] = session_id

    response = http.request("POST", slsc_url, body=json.dumps(close_request))