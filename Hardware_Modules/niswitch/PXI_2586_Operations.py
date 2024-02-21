r"""
"""
TEST_MODULE_NAME = 'PXI-2586'
NB_CHANNELS = 5

import sys
import os

CWD=os.getcwd()
sys.path.append(CWD)

import SelfTest_CF
sys.path.append(os.path.join(CWD,'gRPC_Client','python_sourcefile'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','niswitch'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nidmm'))

import datetime

import grpc
import time
import numpy as np
from Lib import random

import niswitch_pb2 as niswitch_types
import niswitch_pb2_grpc as grpc_niswitch

import nidmm_pb2 as nidmm_types
import nidmm_pb2_grpc as grpc_nidmm

TOPOLOGY_STRING = "2586/5-DPST"
SIMULATION = True
SESSION_NAME = "NI-Switch-Session-1"
Status=None

from DMM_Operations import DMM_Configure_acquisition, DMM_finite_acquisition, DMM_Close

Measurements=[]
grpc_nidmm=None
vi_nidmm=None
dmm_Status=None
average=None
vi_niswitch=None
niswitch_client=None


def PXI_2586_Operations(gRPC_channel, PXI_2586_Device, DMM_ResourceName, DMM_Init_Options, expected_path_resistance):
    """This function performs a series of tests on PXI-2586 module configured in 5-DPST topology. 
        Some external loopbacks are required:
            CH0+ - CH0-
            CH1+ - CH1-
            CH2+ - CH2-
            CH3+ - CH3-
            CH4+ - CH4-
            COM0+ - COM1+ - COM2+ - COM3+ - COM4+
            COM0- - COM1- - COM2- - COM3- - COM4-
    """
    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = TEST_MODULE_NAME
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    #------------------------------ Init PXI-2584  -------------------------------
    MyTestResult=SelfTest_CF.Test_Result()
    MyTestResult.CustomInit('PXI-2586: Configure PXI-2586 in "2586/5-DPST" topology','Fail',1,[0],[0],'This test configures the PXI-2586 in "2586/5-DPST" topology.',str(datetime.datetime.now()))
    MyTestResult.Test_Numeric_Result[0], niswitch_client, vi_niswitch=PXI_2586_Init(gRPC_channel, PXI_2586_Device)
    if  MyTestResult.Test_Numeric_Result[0]==0:
        MyTestResult.Test_PassFail_Status='Pass'
    else:
        MyTestResult.Test_PassFail_Status='Fail'               

    Tests_Result_list.append(MyTestResult)
    del MyTestResult
    #-----------------------------------------------------------------------------


    #------------------------------ Configure DMM  -------------------------------
    MyTestResult=SelfTest_CF.Test_Result()
    MyTestResult.CustomInit('PXI-4080: Configure DMM for 2-Wires Resistor Measurement','Fail',1,[0],[0],'This test configures the PXI-4080 DMM for 2-Wires Resistor measurements.',str(datetime.datetime.now()))
    MyTestResult.Test_Numeric_Result[0], grpc_nidmm, vi_nidmm= DMM_Configure_acquisition(gRPC_channel, DMM_ResourceName, DMM_Init_Options, "2_WIRE_RES")
    if  MyTestResult.Test_Numeric_Result[0]==0:
        MyTestResult.Test_PassFail_Status='Pass'
    else:
        MyTestResult.Test_PassFail_Status='Fail'               

    Tests_Result_list.append(MyTestResult)
    del MyTestResult
    #-----------------------------------------------------------------------------

    try:
        i=0
        for i in range(NB_CHANNELS):
            #---------------------- Close PXI-2586 Relay -----------------------
            MyTestResult=SelfTest_CF.Test_Result()
            channel1="ch"+str(i)
            channel2="com"+str(i)
            MyTestResult.CustomInit('PXI-2586: connect '+channel1+" -> "+channel2,'Fail',1,[0],[0],'This test connects channel '+channel1+ "to channel "+channel2+" from PXI-2586.",str(datetime.datetime.now()))
            MyTestResult.Test_Numeric_Result[PXI_2586_Channel_Action(niswitch_client, vi_niswitch, channel1, channel2, "Connect")]
            if  MyTestResult.Test_Numeric_Result[0]==0:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'               

            Tests_Result_list.append(MyTestResult)
            del MyTestResult  
            #------------------------------ DMM Acquisition  -------------------------------
            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('DMM: '+channel1+" path resistance measurement",'Fail',1,[expected_path_resistance],[0],'This test measures resistance of channel '+channel1+ "to channel "+channel2+" path from PXI-2586.",str(datetime.datetime.now()))
            dmm_Status, Measurements, average=DMM_finite_acquisition(grpc_nidmm,vi_nidmm)

            if dmm_Status==0:
                MyTestResult.Test_Numeric_Result[0]=average
                MyTestResult.Test_Numeric_Expected_Result[0]=expected_path_resistance
                Tests_Status=SelfTest_CF.Test_Numeric_Test(expected_path_resistance,MyTestResult.Test_Numeric_Result[0],5)
                #Tests_Status=SelfTest_CF.Test_Numeric_Test(MyTestResult.Test_Numeric_Result[0],MyTestResult.Test_Numeric_Result[0],5)                
                if Tests_Status==True:
                    MyTestResult.Test_PassFail_Status='Pass'
                else:
                    MyTestResult.Test_PassFail_Status='Fail'
            else:
                MyTestResult.Test_PassFail_Status='Fail'
            Tests_Result_list.append(MyTestResult)
            del MyTestResult
             #---------------------- Open PXI-2586 Relay -----------------------
            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('PXI-2586: disconnect '+channel1+" -> "+channel2,'Fail',1,[0],[0],'This test disconnects channel '+channel1+ "to channel "+channel2+" from PXI-2586.",str(datetime.datetime.now()))
            MyTestResult.Test_Numeric_Result[PXI_2586_Channel_Action(niswitch_client, vi_niswitch, channel1, channel2, "Disconnect")]
            if  MyTestResult.Test_Numeric_Result[0]==0:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'               

            Tests_Result_list.append(MyTestResult)
            del MyTestResult  

    except:
        print(f'PXI-2586 Exception.')

    finally:
        #---------------------- Close NI-DMM session -----------------------
        if vi_nidmm != 0:
            DMM_Close(grpc_nidmm,vi_nidmm)
        if vi_niswitch != 0:
            PXI_2586_Close(niswitch_client, vi_niswitch)            
     
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)

    return My_Module_Result 

def PXI_2586_Channel_Action(niswitch_client, vi_niswitch, channel1, channel2, action):


    def check_for_error(vi_niswitch, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = niswitch_client.ErrorMessage(niswitch_types.ErrorMessageRequest(vi=vi_niswitch, error_code=status))
            raise Exception(error_message_response.error_message)
        return status

    def check_for_initialization_error(response):
        """Raise an exception if an error was returned from Initialize."""
        if response.status < 0:
            raise RuntimeError(f"Error: {response.error_message or response.status}")
        if response.status > 0:
            sys.stderr.write(f"Warning: {response.error_message or response.status}\n")
        return response.status

    try:
        if action=="Connect":
            #Connect channel1 to channel2
            Status=check_for_error(vi_niswitch, (niswitch_client.Connect(niswitch_types.ConnectRequest(vi=vi_niswitch,channel1=channel1,channel2=channel2))).status)
        elif action=="Disconnect":
            #Disconnect ALL
            Status=check_for_error(vi_niswitch, (niswitch_client.DisconnectAll(niswitch_types.DisconnectAllRequest(vi=vi_niswitch))).status)
        else:
            Status=-1
                
    except AttributeError:
        print(f'Attribute Error Exception')
        Status=-3
    except TypeError:
        print(f'TypeError Exception')
        Status=-2
    except Exception:
        print(f'Exception')
        Status=-1
    finally:
        Status=Status
    return Status

def PXI_2586_Init(gRPC_channel, PXI_2586_Device):

    niswitch_client = grpc_niswitch.NiSwitchStub(gRPC_channel)
    def check_for_error(vi_niswitch, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = niswitch_client.ErrorMessage(niswitch_types.ErrorMessageRequest(vi=vi_niswitch, error_code=status))
            raise Exception(error_message_response.error_message)
        return status

    def check_for_initialization_error(response):
        """Raise an exception if an error was returned from Initialize."""
        if response.status < 0:
            raise RuntimeError(f"Error: {response.error_message or response.status}")
        if response.status > 0:
            sys.stderr.write(f"Warning: {response.error_message or response.status}\n")
        return response.status

    #Open session to NI-SWITCH and set topology.
    init_with_topology_response = niswitch_client.InitWithTopology(
        niswitch_types.InitWithTopologyRequest(
            session_name=SESSION_NAME,
            resource_name=PXI_2586_Device,
            topology=TOPOLOGY_STRING,
            simulate=SIMULATION,
            reset_device=True,
        )
    )
    try:
        vi_niswitch = init_with_topology_response.vi
        Status=check_for_initialization_error(init_with_topology_response)

    except AttributeError:
        print(f'Attribute Error Exception')
        Status=-3
    except TypeError:
        print(f'TypeError Exception')
        Status=-2
    except Exception:
        print(f'Exception')
        Status=-1
    finally:
        Status=Status
    return Status, niswitch_client, vi_niswitch

def PXI_2586_Close(niswitch_client, vi_niswitch):


    def check_for_error(vi_niswitch, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = niswitch_client.ErrorMessage(niswitch_types.ErrorMessageRequest(vi=vi_niswitch, error_code=status))
            raise Exception(error_message_response.error_message)
        return status

    def check_for_initialization_error(response):
        """Raise an exception if an error was returned from Initialize."""
        if response.status < 0:
            raise RuntimeError(f"Error: {response.error_message or response.status}")
        if response.status > 0:
            sys.stderr.write(f"Warning: {response.error_message or response.status}\n")
        return response.status

    try:
        if  vi_niswitch.id != 0:
            # close the session.
            niswitch_client.Close(niswitch_types.CloseRequest(vi=vi_niswitch))
            Status=0    
    except AttributeError:
        print(f'Attribute Error Exception')
        Status=-3
    except TypeError:
        print(f'TypeError Exception')
        Status=-2
    except Exception:
        print(f'Exception')
        Status=-1
    finally:
        Status = Status
    return Status