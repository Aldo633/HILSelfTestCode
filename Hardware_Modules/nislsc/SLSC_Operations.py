r"""SLSC Test Module."""

TEST_MODULE_NAME = 'SLSC'

import sys
import os

CWD=os.getcwd()
sys.path.append(CWD)


#sys.path.append(os.path.join(CWD,'gRPC_Client','python_sourcefile'))

import datetime
import urllib3
import json
import SelfTest_CF

init_request = {"id": "Self_Test","jsonrpc": "2.0","method": "initializeSession","params":{"devices": ""}}
close_request = {"id": "Self_Test","jsonrpc": "2.0","method": "closeSession","params":{"session_id": ""}}
get_modules_request = {"id": "Self_Test","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": "Dev.Modules"}}
get_property_request = {"id": "Self_Test","jsonrpc": "2.0","method": "getProperty","params":{"session_id": "","devices":[""],"property": ""}}
execute_reserveDevices_request = {"id": "Self_Test","jsonrpc": "2.0","method": "reserveDevices","params":{"session_id": "","devices":[""],"access":"ReadWrite","reservation_group":"self_test"}}
set_property_request =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","devices":[""],"physical_channels":[""],"property": "","value":None}}
set_LineDirection_property_request =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.Line.Direction","value":None}}
execute_unreserveDevices_request = {"id": "Self_Test","jsonrpc": "2.0","method": "unreserveDevices","params":{"session_id": "","devices":[""]}}
set_property_commit_request = {"id": "Self_Test","jsonrpc": "2.0","method": "commitProperties","params":{"session_id": "","devices":[""]}}
set_property_VsupSelect =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.VsupSelect","value":1}}
set_property_InputThreshold_5V =  {"id": "Self_Test","jsonrpc": "2.0","method": "setProperty","params":{"session_id": "","physical_channels":[""],"property": "NI.InputThreshold5V","value":2.5}}


#Line Direction
Input_Source = 0
Input_Sink = 1
Output_Source = 2
Output_Sink = 3

#import time
#import numpy as np

#response=None
http = urllib3.PoolManager()
slsc_url = ''
SLSC_Devices=[]
SLSC_12202_Devices=[]


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

def SLSC_Operations(SLSC_Chassis_Name):
    """This function interacts with the SLSC chassis: it enumerates modules present in chassis, their location and their type. Then the function configures SLSC-12202 Ports for the Self-Test part (DIOs of RMIO and DIO boards)."""

    # Initialize Parameters
    slsc_url = f'http://{SLSC_Chassis_Name}/nislsc/call'
    session_id = ""

    SLSC_Devices=[]
    SLSC_12202_Devices=[]
    Measurements=[]

    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = TEST_MODULE_NAME
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []

    try:
        # Initialize Session
        init_request['params']['devices'] = SLSC_Chassis_Name
        #response = http.request("POST", slsc_url, body=json.dumps(init_request), retries=2, timeout=5.0)
        response = http.request("POST", slsc_url, body=json.dumps(init_request))
        My_Module_Result.Status_Code,session_id=error_handling(json.loads(response.data.decode()))

        if My_Module_Result.Status_Code==0 and session_id!=None :
            #----------------------------------- TESTS -----------------------------------  
            #---------------------- Find SLSC-12202 Modules -----------------------
            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('List and locate NI-SLSC-12202 Modules','Fail',6,[],[1,2,3,4,5,6],'This test checks how many NI SLSC-12202 are present on system and returns respective slots location.',str(datetime.datetime.now()))
            
            MyTestResult.Test_PassFail_Status,SLSC_12202_Devices,Measurements=List_NI_SLSC_12202_Modules(session_id, slsc_url, SLSC_Chassis_Name, MyTestResult.Test_Expected_Numeric_Results)
            MyTestResult.Test_Numeric_Results.extend(Measurements)

            Tests_Result_list.append(MyTestResult)
            del MyTestResult

            #-------------------- Configure SLSC-12202 Modules ---------------------
                               
            if len(SLSC_12202_Devices)>0:
                #-------------------- SLSC-12202 Modules Reservation ---------------------
                MyTestResult=SelfTest_CF.Test_Result()
                MyTestResult.CustomInit('SLSC-12202 Reservation','Pass',1,[],[0],'The test reserves the detected SLSC-12202 Modules.',str(datetime.datetime.now()))
                
                #Reserve Devices
                execute_reserveDevices_request["params"]["session_id"] = session_id
                execute_reserveDevices_request["params"]["devices"] = SLSC_12202_Devices

                response = http.request("POST", slsc_url, body=json.dumps(execute_reserveDevices_request))
                response_dict = json.loads(response.data)

                if 'error' in response_dict:
                    print(f'Error while reserving module: code: {response_dict["error"]["code"]}, Message: {response_dict["error"]["message"]}.')
                    MyTestResult.Test_PassFail_Status='Fail'
                    MyTestResult.Test_Numeric_Results[0]=response_dict["error"]["code"]
                
                Tests_Result_list.append(MyTestResult)
                del MyTestResult

                #-------- For all SLSC-12202 Modules: set Ports 0 and 2 as Output, set Ports 1 and 3 as Input
                MyTestResult=SelfTest_CF.Test_Result()
                MyTestResult.CustomInit('SLSC-12202 Ports Configuration','Pass',6,[-1,-1,-1,-1,-1,-1],[0,0,0,0,0,0],'The test configures SLSC-12202 Ports for the Self-Test part (DIOs of RMIO and DIO boards).',str(datetime.datetime.now()))                
            
                i=0
                set_LineDirection_property_request["params"]["session_id"] = session_id
                for i in range(len(SLSC_12202_Devices)): 

                    #Measurements.append(0)
                    #---------- "/port0/line0:7" ---------- 
                    set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port0/line0:7"]
                    set_LineDirection_property_request["params"]["value"]=[Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source]

                    response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Lines Direction for "/port0/line0:7" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0
                    #---------- "/port1/line0:7" ---------- 
                    set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port1/line0:7"]
                    set_LineDirection_property_request["params"]["value"]=[Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink]

                    response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Lines Direction for "/port1/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0                    
                    #---------- "/port2/line0:7" ---------- 
                    set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port2/line0:7"]
                    set_LineDirection_property_request["params"]["value"]=[Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source, Output_Source]

                    response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Lines Direction for "/port2/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0                        
                    #---------- "/port3/line0:7" ---------- 
                    set_LineDirection_property_request["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/port3/line0:7"]
                    set_LineDirection_property_request["params"]["value"]=[Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink, Input_Sink]

                    response = http.request("POST", slsc_url, body=json.dumps(set_LineDirection_property_request))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Lines Direction for"/port3/line0:7": error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0
                    i=0
                    for i in range(len(MyTestResult.Test_Numeric_Results)):
                        if MyTestResult.Test_Numeric_Results[i]==0 and MyTestResult.Test_PassFail_Status=='Pass':
                            MyTestResult.Test_PassFail_Status=='Pass'
                        else:
                            MyTestResult.Test_PassFail_Status=='Fail'
                            #break
                    else:
                        MyTestResult.Test_Numeric_Results=[-1,-1,-1,-1,-1,-1]
                        MyTestResult.Test_PassFail_Status='Fail'
                    
                    Tests_Result_list.append(MyTestResult)
                    del MyTestResult
                    
                    #---------- Select Vsup0 for Bank 0----------
                    set_property_VsupSelect["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank0"]

                    response = http.request("POST", slsc_url, body=json.dumps(set_property_VsupSelect))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Vsup for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0

                    #---------- Select Vsup0 for Bank 1----------
                    set_property_VsupSelect["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank1"]

                    response = http.request("POST", slsc_url, body=json.dumps(set_property_VsupSelect))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Vsup for Bank 1" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0
                    
                    #---------- Configure Input Threshold to 2.5V for Bank 0 ---------- 
                    set_property_InputThreshold_5V["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank0"]

                    response = http.request("POST", slsc_url, body=json.dumps(set_property_InputThreshold_5V))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Input Threshold for Bank 0" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0

                    #---------- Configure Input Threshold to 2.5V for Bank 1 ---------- 
                    set_property_InputThreshold_5V["params"]["physical_channels"]=[SLSC_12202_Devices[i]+"/bank1"]

                    response = http.request("POST", slsc_url, body=json.dumps(set_property_InputThreshold_5V))
                    response_dict = json.loads(response.data)

                    if 'error' in response_dict:
                        if 'code' in response_dict["error"]:
                            print(f'Error while setting Input Threshold for Bank 1" : error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                            MyTestResult.Test_Numeric_Results[i]=response_dict["error"]["code"]
                            break
                    else:
                        MyTestResult.Test_Numeric_Results[i]=0                        
                    

                #--------------- Commit ------------------------
                MyTestResult=SelfTest_CF.Test_Result()
                MyTestResult.CustomInit('SLSC-12202 Configuration Commit','Pass',1,[0],[0],'The test commits SLSC-12202 Ports Configuration.',str(datetime.datetime.now()))                

                set_property_commit_request["params"]["session_id"] = session_id
                set_property_commit_request ["params"]["devices"] = SLSC_12202_Devices

                response = http.request("POST", slsc_url, body=json.dumps(set_property_commit_request))
                response_dict = json.loads(response.data)

                if 'error' in response_dict:
                    if 'code' in response_dict["error"]:
                        print(f'Error while applying Device Configuration: error code:{response_dict["error"]["code"]}, Message:{response_dict["error"]["message"]}.')
                        MyTestResult.Test_Numeric_Results=[response_dict["error"]["code"]]
                        MyTestResult.Test_PassFail_Status='Fail'
                
                Tests_Result_list.append(MyTestResult)
                del MyTestResult

                #-------------------- Unreservation SLSC-12202 Modules ---------------------
                MyTestResult=SelfTest_CF.Test_Result()
                MyTestResult.CustomInit('SLSC-12202 Unreservation','Pass',1,[0],[0],'The test unreserves the detected SLSC-12202 Modules.',str(datetime.datetime.now()))                                
                
                execute_unreserveDevices_request['params']['session_id'] = session_id
                execute_unreserveDevices_request["params"]["devices"] = SLSC_12202_Devices

                response = http.request("POST", slsc_url, body=json.dumps(execute_unreserveDevices_request))
                response_dict = json.loads(response.data)

                if 'error' in response_dict:
                    print(f'Error while unreserving module: code: {response_dict["error"]["code"]}, Message: {response_dict["error"]["message"]}.')
                    MyTestResult.Test_Numeric_Results=[response_dict["error"]["code"]]
                    MyTestResult.Test_PassFail_Status='Fail'
                
                Tests_Result_list.append(MyTestResult)
                del MyTestResult

    except urllib3.exceptions.ReadTimeoutError:
        print(f'{"":25}\tERROR\t{"Connection failed, ReadTimeoutError.":60}')       
        My_Module_Result.Status_Code=-3
    except urllib3.exceptions.MaxRetryError:
        print(f'{"":25}\tERROR\t{"Connection failed, MaxRetryError.":60}')
        My_Module_Result.Status_Code=-2
        response=None
    except urllib3.exceptions.NewConnectionError:
        print(f'{"":25}\tERROR\t{"Connection failed, NewConnectionError.":60}')
        My_Module_Result.Status_Code=-1
        response=None

    finally:
        if session_id:
            close_request['params']['session_id'] = session_id
            response = http.request("POST", slsc_url, body=json.dumps(close_request))
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    return My_Module_Result   
