import os
import sys
import grpc
import SelfTest_CF
import SSH_gRPC_Server
import datetime
import urllib3
import json



CWD=os.getcwd()
print(f"CWD:{str(CWD)}")

#File path to serialized JSON results
JSON_TEST_FILE_JSONPICKLE = os.path.join(CWD,'Tests_data_JSONPICKLE.json')
JSON_TEST_FILE_JSON_DUMPS = os.path.join(CWD,'Tests_data_JSON_DUMPS.json')
REPORT_FILE_PATH=os.path.join(CWD,'Report.txt')


sys.path.append(os.path.join(CWD,'gRPC_Client','python_sourcefile'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nislsc'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nifpga'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nidaqmx'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nidcpower'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','KS_N6752A'))

#from SSH_gRPC_Server import Start_gRPC_Server
from SLSC_Operations import SLSC_Operations
from FPGA_RMIO_Operations import FPGA_RMIO_Operations
from FPGA_RDIO_Operations import FPGA_RDIO_Operations
from PXIe_6738_Operations import PXIe_6738_Operations
from PXIe_4322_Operations import PXIe_4322_Operations
from PXIe_4136_Operations import PXIe_4136_Operations

#gRPC Server


#FPGA RMIO
RMIO_Bitfile_Path = "//home//admin//FPGA_Bitfiles//PXIe7846R_SelfTest.lvbitx"
RMIO_Bitfile_Signature = "5F1413A25569133829C69232D595A53A"
RMIO_FPGA_ResourceName = "PXI1Slot2"
#FPGA RDIO
RDIO_Bitfile_Path = "//home//admin//FPGA_Bitfiles//PXIe7820R_SelfTest.lvbitx"
RDIO_Bitfile_Signature = "C8C05D6D335094892D20B78090AF3087"
RDIO_FPGA_ResourceName = "PXI1Slot3"
#Analog Output Boards
PXIe_6738_Device = "PXI1Slot4"
PXIe_4322_Device = "PXI1Slot7"

#Analog Input Boards
PXIe_4303_Device = "PXI1Slot10"

FPGA_Main_ControlBool_Start = 0x1800E
FPGA_Main_ControlBool_Stop = 0x18012

FPGA_Main_IndicatorArrayI64_AIs = 0x18000
FPGA_Main_IndicatorArrayI64Size_AIs = 8

FPGA_Main_ControlU8_Connector0Port_0 = 0x18006
FPGA_Main_ControlU8_Connector1Port_0 = 0x1801E
FPGA_Main_ControlU8_Connector1Port_2 = 0x18026

FPGA_Main_IndicatorU8_Connector0Port_1 = 0x1800A
FPGA_Main_IndicatorU8_Connector1Port_1 = 0x18022
FPGA_Main_IndicatorU8_Connector1Port_3 = 0x1802A

PXIe_6738_Channels_First_Test=[0]
CurrentOutputValue = [5]

import datetime


import nifpga_pb2 as nifpga_types
import nifpga_pb2_grpc as grpc_nifpga
import nidaqmx_pb2 as nidaqmx_types
import nidaqmx_pb2_grpc as grpc_nidaqmx
import time
import numpy as np


def Create_Channels_String(Device_Resource_Name, Channels):
    """This function prepares the NI-DAQmx channels string."""
    i=0
    Channels_String=''
    for i in range(len(Channels)):
        Channels_String=Channels_String+ Device_Resource_Name + "/ao" + str(Channels[i])
        if i<len(Channels)-1:
            Channels_String=Channels_String+","
        i=i+1
    return Channels_String

def List_NI_SLSC_12202_Modules(session_id, slsc_url, slsc_chassis_name, Test_Numeric_Expected_Result):
    #Test_Status=False
    Measurements=[]
    # Get Modules in Chassis
    get_modules_request["params"]["session_id"] = session_id
    get_modules_request["params"]["devices"] = [slsc_chassis_name]

    response = http.request("POST", slsc_url, body=json.dumps(get_modules_request))
    Status, resultsValue = error_handling_WithResultValue(json.loads(response.data))

    if len(resultsValue)>0:
        #print(f'Modules detected:\n{resultsValue}')
        i=0
        SLSC_Devices.extend(resultsValue)
        #Get list of SLSC-12202 Modules
        for i in range(len(SLSC_Devices)):
            #Get Product Name
            get_property_request["params"]["session_id"] = session_id
            get_property_request["params"]["devices"] = [SLSC_Devices[i]]
            get_property_request["params"]["property"] = "Dev.ProductName"
            response = http.request("POST", slsc_url, body=json.dumps(get_property_request))
            response_dict = json.loads(response.data)
            device_ProductName = str(response_dict["result"]["value"])
            if device_ProductName.find('SLSC-12202')!=-1:
                #Get Slot Number
                SLSC_12202_Devices.append(SLSC_Devices[i])
                get_property_request["params"]["session_id"] = session_id
                get_property_request["params"]["devices"] = [SLSC_Devices[i]]
                get_property_request["params"]["property"] = "Dev.SlotNum"
                response = http.request("POST", slsc_url, body=json.dumps(get_property_request))
                response_dict = json.loads(response.data)
                device_Slot = response_dict["result"]["value"][0]
                Measurements.append(device_Slot)

                
                

                
            else:
                Measurements.append(-1)
        #print(f'NB Modules NI SLSC-12202 found in setup: {len(SLSC_12202_Devices)}.')
        print(f'{"":25}\tDEBUG\t{"NB Modules NI SLSC-12202 found in setup: {len(SLSC_12202_Devices)}.":60}')    
      
    #We compute Test Status
    if Measurements==Test_Numeric_Expected_Result:
        Status='Pass'
    else:
        Status='Fail'   
    return Status,SLSC_12202_Devices,Measurements

def error_handling(response_dict):
    """This function handles the error after a HTTP Request."""
    Status=0
    session_id=None
    if 'result' in response_dict:
        if 'session_id' in response_dict['result']:
            session_id=response_dict['result']['session_id']
            Status=0
    if 'error' in response_dict:
        if 'code' in response_dict['error'] and 'message' in response_dict['error']:
            if  response_dict['error']['code']==-32000 and response_dict['error']['message']=='SLSC error.':
                print(f"SLSC Error: code: {response_dict['error']['data']['nislsc_code']}, Error Message: {response_dict['error']['data']['nislsc_message']}.")
                Status=response_dict['error']['data']['nislsc_code']  
        else:
            Status=response_dict['error']['code']
    return Status, session_id

def error_handling_WithResultValue(response_dict):
    """This function handles the error after a HTTP Request."""
    Status=0
    resultsValue=None
    if 'result' in response_dict:
        if 'value' in response_dict['result']:
            resultsValue=response_dict['result']['value']
        if 'data' in response_dict['result']:
            resultsValue=response_dict['result']['data']           
    if 'error' in response_dict:
        Status=response_dict['error']['code']  
    return Status, resultsValue


def U8_Digital_Port_Operations(nifpga_client, FPGA_session, FPGA_Control_ID, FPGA_Indicator_ID, Values_to_Write):
    """This function performs a series of write/read operations on a U8 digital port and performs a Pass/Fail Test at the end."""
    i=0
    Test_Status=True
    Measurements=[]
    for i in range(len(Values_to_Write)):
        #Write Port 0
        response=nifpga_client.WriteU8(
            nifpga_types.WriteU8Request(
                session=FPGA_session,
                control = FPGA_Control_ID,
                value = Values_to_Write[i],
            )
        )
        raise_if_error(response)
        
        #Read Port 1
        response=nifpga_client.ReadU8(
            nifpga_types.ReadU8Request(
                session=FPGA_session,
                indicator = FPGA_Indicator_ID,
            )
        )
        raise_if_error(response)
        Measurements.append(response.value)
        #Check Measurement
        if Measurements[i]!=Values_to_Write[i]:
            #Measurement is incorrect
            Test_Status=False
        i=i+1
    #We compute Test Status
    if Test_Status==True:
        Status='Pass'
    else:
        Status='Fail'   
    return Status,Measurements;

def raise_if_error(response):
    """Raise an exception if an error was returned."""
    if response.status != 0:
        if response.status > 0:
          print(f'{"":25}\tWARN.\tFPGA RDIO, code: {response.status}.')    
        else:
            raise Exception(f"Error: {response.status}")
    Status = response.status
    return Status


#gRPC Server
ServerIP="192.168.0.51"
ServerPort = 31763
gRPC_channel=None
gRPC_ServerMachine_UserName = 'admin'
gRPC_ServerMachine_Password = ''


#SLSC Chassis
#SLSC_Chassis_Name = "SLSC_XXXXXXXX"
#SLSC_Chassis_Name = "SLSC-12001-032A1EC1" #System2
SLSC_Chassis_Name = "SLSC-12001-032B49E9" #System1
SLSC_IP_Address = "192.168.0.53" #Static IP Address for the chassis

#SLSC_Operations(SLSC_Chassis_Name)
#SelfTest_CF.My_Modules_Results.append(SLSC_Operations(SLSC_Chassis_Name))


CWD=os.getcwd()
sys.path.append(CWD)


#sys.path.append(os.path.join(CWD,'gRPC_Client','python_sourcefile'))



init_request = {"id": "Self_Test","jsonrpc": "2.0","method": "initializeSession","params":{"devices": ""}}
close_request = {"id": "Self_Test","jsonrpc": "2.0","method": "closeSession","params":{"session_id": ""}}
get_modules_request = {"id": "Self_Test","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": "Dev.Modules"}}
get_property_request = {"id": "Self_Test","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": ""}}
get_property_request2 = {"id": "Self_Test","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","physical_channels":[""],"property": ""}}
execute_reserveDevices_request = {"id": "Self_Test","jsonrpc": "2.0","method": "reserveDevices","params":{"session_id": "","devices":[""],"access":"ReadWrite","reservation_group":"self_test"}}
set_property_request =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","devices":[""],"property": "","value":None}}
set_LineDirection_property_request =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.Line.Direction","value":None}}
execute_unreserveDevices_request = {"id": "Self_Test","jsonrpc": "2.0","method": "unreserveDevices","params":{"session_id": "","devices":[""]}}
set_property_commit_request = {"id": "Self_Test","jsonrpc": "2.0","method": "commitProperties","params":{"session_id": "","devices":[""]}}
set_property_VsupSelect =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.VsupSelect","value":1}}
set_property_ni_enable5Vrange =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.RangeEnable5V","value":True}}
set_property_InputThreshold_5V =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.InputThreshold5V","value":2.5}}
update_channel_configuration = {"id": "Self_Test","jsonrpc": "2.0","method": "executeCommand","params":{"session_id": "","devices":[""],"command":"NI.UpdateChannelConfiguration"}}
update_test_mode = {"id": "Self_Test","jsonrpc": "2.0","method": "executeCommand","params":{"session_id": "","devices":[""],"command":"NI.UpdateTestMode"}}
#Line Direction
Input_Source = 0
Input_Sink = 1
Output_Source = 2
Output_Sink = 3
Output_PushPull = 4
Channel_Disconnect = 5

SelfTest_CF.My_Modules_Results=[]


#import time
import numpy as np
#SSH_gRPC_Server.Start_gRPC_Server(ServerIP, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password)

##Init SLSC
#response=None
http = urllib3.PoolManager()
slsc_url = f'http://{SLSC_IP_Address}/nislsc/call'
session_id = ""
SLSC_Devices=[]
SLSC_12202_Devices=[]

init_request['params']['devices'] = SLSC_Chassis_Name
response = http.request("POST", slsc_url, body=json.dumps(init_request))
error_code,session_id=error_handling(json.loads(response.data.decode()))

PassFailStatus,SLSC_12202_Devices, Measurements = List_NI_SLSC_12202_Modules(session_id, slsc_url, SLSC_Chassis_Name, 5)

if len(SLSC_12202_Devices)>0:
    #Reserve Devices
    execute_reserveDevices_request["params"]["session_id"] = session_id
    execute_reserveDevices_request["params"]["devices"] = SLSC_12202_Devices
    response = http.request("POST", slsc_url, body=json.dumps(execute_reserveDevices_request))
    response_dict = json.loads(response.data)
    if 'error' in response_dict:
        print(f'Error while reserving module: code: {response_dict["error"]["code"]}, Message: {response_dict["error"]["message"]}.')

    for i in range(len(SLSC_12202_Devices)):
        #Check Vsup1 status
        get_property_request["params"]["session_id"] = session_id
        get_property_request["params"]["devices"] = [SLSC_12202_Devices[i]]
        get_property_request["params"]["property"] = "NI.StatusVsup_0PowerGood"
        response = http.request("POST", slsc_url, body=json.dumps(get_property_request))
        response_dict = json.loads(response.data)
        Vsup0Status = response_dict["result"]["value"][0]

        get_property_request["params"]["session_id"] = session_id
        get_property_request["params"]["devices"] = [SLSC_12202_Devices[i]]
        get_property_request["params"]["property"] = "NI.StatusVsup_1PowerGood"
        response = http.request("POST", slsc_url, body=json.dumps(get_property_request))
        response_dict = json.loads(response.data)
        Vsup1Status = response_dict["result"]["value"][0]

        #Enable test mode
        
        set_property_request["params"]["session_id"] = session_id
        set_property_request["params"]["devices"] = [SLSC_12202_Devices[i]]
        set_property_request["params"]["property"] = "NI.TestModeEnable"
        set_property_request["params"]["value"]=[False]
        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)

        set_property_request["params"]["session_id"] = session_id
        set_property_request["params"]["devices"] = [SLSC_12202_Devices[i]]
        set_property_request["params"]["property"] = "NI.TestModeValue"
        set_property_request["params"]["value"]=[0]
        response = http.request("POST", slsc_url, body=json.dumps(set_property_request))
        response_dict = json.loads(response.data)
        
        #Setting direction Loopback 0-1
        set_LineDirection_property_request["params"]["session_id"] = session_id    
        set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port0/line0:7"]
        set_LineDirection_property_request["params"]["value"]=[Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,]
        response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
        response_dict = json.loads(response.data)

        set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port1/line0:7"]
        set_LineDirection_property_request["params"]["value"]=[Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,]
        response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for "/port0/line0:7" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        
        #Setting direction Loopback 2-3
        set_LineDirection_property_request["params"]["session_id"] = session_id    
        set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port2/line0:7"]
        set_LineDirection_property_request["params"]["value"]=[Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,Output_Source,]
        response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
        response_dict = json.loads(response.data)

        set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port3/line0:7"]
        set_LineDirection_property_request["params"]["value"]=[Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,Input_Sink,]
        response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Lines Direction for "/port0/line0:7" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        
    #Enabling Test Mode
    
    
        #---------- Select Vsup0 for Bank 0----------
        set_property_VsupSelect["params"]["session_id"] = session_id
        set_property_VsupSelect["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank0"]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_VsupSelect))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Vsup for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')

        #---------- Select Threshold for Bank 0----------
        set_property_ni_enable5Vrange["params"]["session_id"] = session_id
        set_property_ni_enable5Vrange["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank0"]
        response = http.request("POST", slsc_url, body=json.dumps(set_property_ni_enable5Vrange))
        response_dict = json.loads(response.data)

        
        set_property_InputThreshold_5V["params"]["session_id"] = session_id
        set_property_InputThreshold_5V["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank0"]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_InputThreshold_5V))
        response_dict = json.loads(response.data)
        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Input Threshold for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
        
        #---------- Select Vsup0 for Bank 1----------
        set_property_VsupSelect["params"]["session_id"] = session_id
        set_property_VsupSelect["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank1"]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_VsupSelect))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Vsup for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')

        #---------- Select Threshold for Bank 1----------
        set_property_ni_enable5Vrange["params"]["session_id"] = session_id
        set_property_ni_enable5Vrange["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank1"]
        response = http.request("POST", slsc_url, body=json.dumps(set_property_ni_enable5Vrange))
        response_dict = json.loads(response.data)

        
        set_property_InputThreshold_5V["params"]["session_id"] = session_id
        set_property_InputThreshold_5V["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank1"]

        response = http.request("POST", slsc_url, body=json.dumps(set_property_InputThreshold_5V))
        response_dict = json.loads(response.data)
        if 'error' in response_dict:
            if 'code' in response_dict["error"]:
                print(f'Error while setting Input Threshold for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')


        #Getting lineindex
        get_property_request2["params"]["session_id"] = session_id
        get_property_request2["params"]["physical_channels"] = [SLSC_Devices[i]+"/port0/line0"]
        get_property_request2["params"]["property"] = "NI.Line.Index"
        response = http.request("POST", slsc_url, body=json.dumps(get_property_request2))
        response_dict = json.loads(response.data)
        LineIndexport0_0 = response_dict["result"]["value"][0]
        #Update Channel Configuration
        update_channel_configuration["params"]["session_id"] = session_id
        update_channel_configuration ["params"]["devices"] = SLSC_12202_Devices[i]   

        response = http.request("POST", slsc_url, body=json.dumps(update_channel_configuration))
        response_dict = json.loads(response.data)

        if 'error' in response_dict:
         if 'code' in response_dict["error"]:
            print(f'Error while applying update channel config: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')




   
    #--------------- Commit ------------------------
    set_property_commit_request["params"]["session_id"] = session_id
    set_property_commit_request ["params"]["devices"] = SLSC_12202_Devices

    response = http.request("POST", slsc_url, body=json.dumps(set_property_commit_request))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        if 'code' in response_dict["error"]:
            print(f'Error while applying Device Configuration: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
    

    update_channel_configuration["params"]["session_id"] = session_id
    update_channel_configuration ["params"]["devices"] = SLSC_12202_Devices[0]   

    response = http.request("POST", slsc_url, body=json.dumps(update_channel_configuration))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        if 'code' in response_dict["error"]:
            print(f'Error while applying update channel config: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')

    update_test_mode["params"]["session_id"] = session_id
    update_test_mode ["params"]["devices"] = SLSC_12202_Devices[0]   

    response = http.request("POST", slsc_url, body=json.dumps(update_test_mode))
    response_dict = json.loads(response.data)

    if 'error' in response_dict:
        if 'code' in response_dict["error"]:
            print(f'Error while applying update test mode: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')

    #--------------- Unreserve ------------------------
    

try:
    gRPC_channel = grpc.insecure_channel(f"{ServerIP}:{ServerPort}")
    grpc.channel_ready_future(gRPC_channel).result(timeout=3.0)
except grpc.FutureTimeoutError:
    SelfTest_CF.Display_Debug_Info('Error, tinmeout: unable to connecto to gRPC Server.')
else:
    #**************************************************** Manual test with 6738 into SLSC*************************************************
    # Create a FPGA client.
    nifpga_client = grpc_nifpga.NiFpgaStub(gRPC_channel)
    daqmx_client = grpc_nidaqmx.NiDAQmxStub(gRPC_channel)
    task = None
    #task = None
    FPGA_session = None
    Measurements=[]
    
    def raise_if_error_daqmx(response):
       """Raise an exception if an error was returned."""
       if response.status != 0:
           response = daqmx_client.GetErrorString(
               nidaqmx_types.GetErrorStringRequest(error_code=response.status)
           )
           raise Exception(f"Error: {response.error_string}")

    try:
        response = nifpga_client.Open(
            nifpga_types.OpenRequest(
                session_name="my FPGA session",
                bitfile=RMIO_Bitfile_Path,
                signature=RMIO_Bitfile_Signature,
                resource=RMIO_FPGA_ResourceName,
                attribute_mapped= nifpga_types.OPEN_ATTRIBUTE_NoRun,
            )
        )

        FPGA_session = response.session
        response = daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-6738 Task"))
        task = response.task
        raise_if_error_daqmx(
            daqmx_client.CreateAOVoltageChan(
                nidaqmx_types.CreateAOVoltageChanRequest(
                    task=task,
                    physical_channel=Create_Channels_String(PXIe_6738_Device,PXIe_6738_Channels_First_Test),
                    min_val=-10.0,
                    max_val=10.0,
                    units=nidaqmx_types.VOLTAGE_UNITS2_VOLTS,
                )
            )
        )
        raise_if_error_daqmx(daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task)))

        Status_Code=raise_if_error(response)
        
    
        response=nifpga_client.Run(
           nifpga_types.RunRequest(
               session=FPGA_session,
               attribute=nifpga_types.RUN_ATTRIBUTE_UNSPECIFIED,
               #attribute_raw=0,
           )
        )
        Status_Code=raise_if_error(response)

        #Start Bitfile
        response=nifpga_client.WriteBool(
            nifpga_types.WriteBoolRequest(
                session=FPGA_session,
                control = FPGA_Main_ControlBool_Start,
                value = 1,
            )
        )
        Status_Code=raise_if_error(response)

        nifpga_client.WriteU8(
            nifpga_types.WriteU8Request(
                session=FPGA_session,
                control = FPGA_Main_ControlU8_Connector1Port_0,
                value = 0xFF,
                )
        )
        raise_if_error(response)

        raise_if_error_daqmx(
            daqmx_client.WriteAnalogF64(
                nidaqmx_types.WriteAnalogF64Request(
                    task=task,
                    num_samps_per_chan=1,
                    data_layout=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,
                    write_array=CurrentOutputValue,
                    timeout=10.0,
                )
            )
        )

        response=nifpga_client.ReadU8(
            nifpga_types.ReadU8Request(
                session=FPGA_session,
                indicator = FPGA_Main_IndicatorU8_Connector1Port_1,
            )
        )
        raise_if_error(response)
        Measurements.append(response.value)



    except:
        #error_message = rpc_error.details()
        Status_Code=response.status
        print(f'{"":25}\tERROR\tFPGA RDIO Exception, error code: {response.status}.')

    finally:
        if FPGA_session:
            nifpga_client.Close(
                nifpga_types.CloseRequest(
                    session=FPGA_session,
                    attribute=nifpga_types.CLOSE_ATTRIBUTE_UNSPECIFIED,
                    #attribute=nifpga_types.CLOSE_ATTRIBUTE_NoResetIfLastSession,
                )
            )

    if task:
            daqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=task))
            daqmx_client.ClearTask(nidaqmx_types.ClearTaskRequest(task=task))


    #**************************************************** FPGA RMIO *************************************************
    #SelfTest_CF.Display_Debug_Info('FPGA RMIO Test Module: started.')
    #SelfTest_CF.My_Modules_Results.append(FPGA_RMIO_Operations(gRPC_channel, RMIO_FPGA_ResourceName, RMIO_Bitfile_Path, RMIO_Bitfile_Signature))
    #SelfTest_CF.Display_Debug_Info('FPGA RMIO Module: completed.')

    # #**************************************************** FPGA RDIO *************************************************
    #SelfTest_CF.Display_Debug_Info('FPGA RDIO Test Module: started.')
    #SelfTest_CF.My_Modules_Results.append(FPGA_RDIO_Operations(gRPC_channel, RDIO_FPGA_ResourceName, RDIO_Bitfile_Path, RDIO_Bitfile_Signature))
    #SelfTest_CF.Display_Debug_Info('FPGA RDIO Module: completed.')

    # #**********************************************  Analog Outputs Boards ******************************************
    #SelfTest_CF.Display_Debug_Info('PXIe-6738 Test Module: started.')
    #SelfTest_CF.My_Modules_Results.append(PXIe_6738_Operations(gRPC_channel, PXIe_6738_Device, PXIe_4303_Device))
    #SelfTest_CF.Display_Debug_Info('PXIe-6738 Test Module: completed.')

    #SelfTest_CF.Display_Debug_Info('PXIe-4322 Test Module: started.')
    #SelfTest_CF.My_Modules_Results.append(PXIe_4322_Operations(gRPC_channel, PXIe_4322_Device, PXIe_6738_Device))
    #SelfTest_CF.Display_Debug_Info('PXIe-4322 Test Module: completed.')
execute_unreserveDevices_request['params']['session_id'] = session_id
execute_unreserveDevices_request["params"]["devices"] = SLSC_12202_Devices

response = http.request("POST", slsc_url, body=json.dumps(execute_unreserveDevices_request))
response_dict = json.loads(response.data)

execute_unreserveDevices_request['params']['session_id'] = session_id
execute_unreserveDevices_request["params"]["devices"] = SLSC_Chassis_Name

response = http.request("POST", slsc_url, body=json.dumps(execute_unreserveDevices_request))
response_dict = json.loads(response.data)
    


