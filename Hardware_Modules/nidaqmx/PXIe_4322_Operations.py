r"""PXIe-4322 Test Module."""

TEST_MODULE_NAME = 'PXIe-4322'
NB_CHANNELS = 8
Minimal_Value = -4.0
Voltage_Increment = 1.0

PXIe_4322_Channels=[0,1,2,3,4,5,6,7]
PXIe_4303_Channels=[3,7,11,15,19,23,27,31]

import sys
import os

CWD=os.getcwd()
sys.path.append(CWD)

import SelfTest_CF
# sys.path.append(os.path.join(CWD,'Python','gRPC_Client','python_sourcefile'))
# sys.path.append(os.path.join(CWD,'Python','Hardware_Modules','nidaqmx'))

import datetime

import grpc
import nidaqmx_pb2 as nidaqmx_types
import nidaqmx_pb2_grpc as grpc_nidaqmx
import time
import numpy as np
import random

from PXIe_4303_Operations import PXIe_4303_Operations

Measurements=[]
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

def Create_Test_Module_Description_String(PXIe_4322_Channels, CurrentOutputValue, PXIe_4303_Channels):
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
    Description_String=Description_String+'] of PXIe-4322 and measures actual value using following PXIe-4303 channels: ['
    i=0
    for i in range(len(PXIe_4322_Channels)):
        Description_String=Description_String+ str(PXIe_4303_Channels[i])
        if i <len(PXIe_4322_Channels)-1:
            Description_String=Description_String+","
        i=i+1

    Description_String=Description_String+'].'
    return Description_String

def PXIe_4322_Operations(gRPC_channel, PXIe_4322_Device, PXIe_4303_Device):
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

        #---------------------- AO Channels Test -----------------------
        response = daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-4322 Task"))
        raise_if_error_daqmx(response)
        task = response.task
        i=0
        CurrentOutputValue =[]
        MeasuredValue = []
        for i in range(len(PXIe_4322_Channels)):
            CurrentOutputValue.append((float) (Minimal_Value+i*Voltage_Increment))
            MeasuredValue.append(9999.9)
            i=i+1
        MyTestResult=SelfTest_CF.Test_Result()
        MyTestResult.CustomInit('PXIe-4322: check channels','Fail',8,MeasuredValue,CurrentOutputValue,Create_Test_Module_Description_String(PXIe_4322_Channels, CurrentOutputValue, PXIe_4303_Channels),str(datetime.datetime.now()))
        
        raise_if_error_daqmx(
            daqmx_client.CreateAOVoltageChan(
                nidaqmx_types.CreateAOVoltageChanRequest(
                    task=task,
                    physical_channel=Create_Channels_String(PXIe_4322_Device, PXIe_4322_Channels),
                    min_val=-10.0,
                    max_val=10.0,
                    units=nidaqmx_types.VOLTAGE_UNITS2_VOLTS,
                )
            )
        )

        raise_if_error_daqmx(daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task)))

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

        #----------------------------------------------- PXIe-4303 Acquisition  ------------------------------------------------
        PXIe_4303_Status, Measurements, average=PXIe_4303_Operations(gRPC_channel, PXIe_4303_Device, PXIe_4303_Channels)
        #-----------------------------------------------------------------------------------------------------------------------
        Test_Status=True
        if PXIe_4303_Status==0:
            i=0
            for i in range(len(CurrentOutputValue)):
                MyTestResult.Test_Numeric_Results[i]=average[i]
                Test_Status=Test_Status and SelfTest_CF.Test_Numeric_Test(CurrentOutputValue[i],MyTestResult.Test_Numeric_Results[i],1)
            if Test_Status==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'
        else:
            MyTestResult.Test_PassFail_Status='Fail'
        Tests_Result_list.append(MyTestResult)
        del MyTestResult            
 
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