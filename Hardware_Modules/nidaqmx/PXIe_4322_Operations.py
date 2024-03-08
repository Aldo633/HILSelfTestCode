r"""PXIe-4322 Test Module."""

TEST_MODULE_NAME = 'PXIe-4322'
NB_CHANNELS = 8
Minimal_Value = -4.0
Voltage_Increment = 1.0

PXIe_4322_Channels=[0,1,2,3,4,5,6,7]
#PXIe_4303_Channels=[3,7,11,15,19,23,27,31]
PXIe_6738_DI_Channels="port1"
NB_Tests=2
#NB_Output_Values_Per_Test=8
Analog_Output_Values=[3.3,0.0,3.3,0.0,3.3,0.0,3.3,0.0,0.0,3.3,0.0,3.3,0.0,3.3,0.0,3.3]
Expected_DI_Values=[85,170]

import sys
import os

CWD=os.getcwd()
sys.path.append(CWD)

import SelfTest_CF
import datetime

import grpc
import nidaqmx_pb2 as nidaqmx_types
import nidaqmx_pb2_grpc as grpc_nidaqmx
import time
import numpy as np
import random

from PXIe_6738_DI_Operations import PXIe_6738_DI_Operations

Measurements=None
grpc_nidmm=None
vi_nidmm=None
dmm_Status=None
average=None

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

def Create_Test_Module_Description_String(PXIe_4322_Channels, CurrentOutputValue, PXIe_6738_DI_Channels):
    """This function returns the Test Module Description String based on the list of Channels passed as argument."""
    i=0
    Description_String='This test outputs ['
    for i in range(len(PXIe_4322_Channels)):
        Description_String=Description_String+ str(CurrentOutputValue[i])
        if i <len(PXIe_4322_Channels)-1:
            Description_String=Description_String+","
        i=i+1
    Description_String=Description_String+'] Volts on channels ['
    i=0
    for i in range(len(PXIe_4322_Channels)):
        Description_String=Description_String+ str(PXIe_4322_Channels[i])
        if i <len(PXIe_4322_Channels)-1:
            Description_String=Description_String+","
        i=i+1
    Description_String=Description_String+'] of PXIe-4322 and measures actual value using following PXIe-6738 Digital Input Port: '+str(PXIe_6738_DI_Channels)+'.'
    return Description_String

def PXIe_4322_Operations(gRPC_channel, PXIe_4322_Device, PXIe_6738_Device):
    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = TEST_MODULE_NAME
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    # Create a client.
    daqmx_client = grpc_nidaqmx.NiDAQmxStub(gRPC_channel)
    task = None

    def raise_if_error_daqmx(response):
        """Raise an exception if an error was returned."""
        if response.status != 0:
            response = daqmx_client.GetErrorString(
                nidaqmx_types.GetErrorStringRequest(error_code=response.status)
            )
            raise Exception(f"Error: {response.error_string}")
    try:
        response = daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-4322 Task"))
        raise_if_error_daqmx(response)
        task = response.task
        raise_if_error_daqmx(daqmx_client.CreateAOVoltageChan(nidaqmx_types.CreateAOVoltageChanRequest(task=task,physical_channel=Create_Channels_String(PXIe_4322_Device, PXIe_4322_Channels),min_val=-10.0,max_val=10.0,units=nidaqmx_types.VOLTAGE_UNITS2_VOLTS)))
        raise_if_error_daqmx(daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task)))
        j=0
        for j in range(NB_Tests):
            #---------------------- AO Channels Test -----------------------
            MyTestResult=SelfTest_CF.Test_Result()
            CurrentOutputValue =Analog_Output_Values[j*NB_CHANNELS: (j*NB_CHANNELS)+NB_CHANNELS]
               
            MyTestResult.CustomInit('PXIe-4322: check channels, Value: '+hex(Expected_DI_Values[j]),'Fail',1,[-1],[Expected_DI_Values[j]],Create_Test_Module_Description_String(PXIe_4322_Channels, CurrentOutputValue, PXIe_6738_DI_Channels),str(datetime.datetime.now()))
            
            raise_if_error_daqmx(daqmx_client.WriteAnalogF64(nidaqmx_types.WriteAnalogF64Request(task=task,num_samps_per_chan=1,data_layout=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,write_array=CurrentOutputValue,timeout=10.0)))

            #----------------------------------------------- PXIe-6738 DI Acquisition  ------------------------------------------------
            Measurements=None
            PXIe_6738_DI_Status, Measurements=PXIe_6738_DI_Operations(gRPC_channel, PXIe_6738_Device, PXIe_6738_DI_Channels)
            #-----------------------------------------------------------------------------------------------------------------------

            if PXIe_6738_DI_Status==0:
                MyTestResult.Test_Numeric_Results[0]=Measurements[0]
                if Measurements[0]==Expected_DI_Values[j]:
                    MyTestResult.Test_PassFail_Status='Pass'
                else:
                    MyTestResult.Test_PassFail_Status='Fail'
            Tests_Result_list.append(MyTestResult)
            del MyTestResult            
 
        # if task:
        #     daqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=task))
            
        #We output 0.0 volts on all channels.
        #raise_if_error_daqmx(daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task)))
        Zero_Values=[0.0]*len(PXIe_4322_Channels)
        raise_if_error_daqmx(
            daqmx_client.WriteAnalogF64(
                nidaqmx_types.WriteAnalogF64Request(
                    task=task,
                    num_samps_per_chan=1,
                    data_layout=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,
                    write_array=Zero_Values,
                    timeout=10.0,
                )
            )
        )            
        time.sleep(0.5)
        if task:
            daqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=task))
            daqmx_client.ClearTask(nidaqmx_types.ClearTaskRequest(task=task))            
    except:
    #     print(f'PXIe-4322 Exception.')
        print(f'{"":25}\tERROR\t{"PXIe-4322 Exception.":60}')    

    finally:  
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)

    return My_Module_Result 