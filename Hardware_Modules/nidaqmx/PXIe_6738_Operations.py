r"""PXIe-6738 Test Module."""

TEST_MODULE_NAME_PREFIX = 'PXIe-6738'
PXIe_6738_Channels_First_Test=[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,28,29,30]
PXIe_4303_Channels_First_Test=[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,28,29,30]

# PXIe_6738_Channels_Second_Test=[30,31]
# PXIe_4303_Channels_Second_Test=[30,31]

Minimal_Value = -6.0
Voltage_Increment = 0.50

import sys
import os
import SelfTest_CF


import datetime

import grpc
import nidaqmx_pb2 as nidaqmx_types
import nidaqmx_pb2_grpc as grpc_nidaqmx
import time
#import numpy as np
#import random

from PXIe_4303_Operations import PXIe_4303_Operations

Measurements=[]
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

def Create_Test_Module_Description_String(PXIe_6738_Channels, CurrentOutputValue, PXIe_4303_Channels):
    """This function returns the Test Module Description String based on the list of Channels passed as argument."""
    i=0
    Description_String='This test outputs ['
    for i in range(len(PXIe_6738_Channels)):
        Description_String=Description_String+ str(CurrentOutputValue[i])
        if i <len(PXIe_6738_Channels)-1:
            Description_String=Description_String+","
        i=i+1
    Description_String=Description_String+'] Volts on channels ['
    i=0
    for i in range(len(PXIe_6738_Channels)):
        Description_String=Description_String+ str(PXIe_6738_Channels[i])
        if i <len(PXIe_6738_Channels)-1:
            Description_String=Description_String+","
        i=i+1
    Description_String=Description_String+'] of PXIe-6738 and measures actual value using following PXIe-4303 channels: ['
    i=0
    for i in range(len(PXIe_6738_Channels)):
        Description_String=Description_String+ str(PXIe_4303_Channels[i])
        if i <len(PXIe_6738_Channels)-1:
            Description_String=Description_String+","
        i=i+1

    Description_String=Description_String+'].'
    return Description_String

def PXIe_6738_Operations(gRPC_channel, PXIe_6738_Device, PXIe_4303_Device):
    
    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = TEST_MODULE_NAME_PREFIX
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    # Create a gRPC channel + client.
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
        #------------------------------ AO Channels First Series of Test --------------------------------
        response = daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-6738 Task"))
        raise_if_error_daqmx(response)
        task = response.task
        i=0
        CurrentOutputValue =[]
        MeasuredValue = []
        #print(f"NB Channels:", str(len(PXIe_6738_Channels_First_Test)))
        for i in range(len(PXIe_6738_Channels_First_Test)):
            CurrentOutputValue.append((float) (Minimal_Value+i*Voltage_Increment))
            MeasuredValue.append(9999.9)
            i=i+1

        MyTestResult=SelfTest_CF.Test_Result()
        MyTestResult.CustomInit('PXIe-6738: check Channels','Fail',len(PXIe_6738_Channels_First_Test),MeasuredValue, CurrentOutputValue,Create_Test_Module_Description_String(PXIe_6738_Channels_First_Test, CurrentOutputValue, PXIe_4303_Channels_First_Test),str(datetime.datetime.now()))
        
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
        PXIe_4303_Status, Measurements, average=PXIe_4303_Operations(gRPC_channel, PXIe_4303_Device, PXIe_4303_Channels_First_Test)
        #-----------------------------------------------------------------------------------------------------------------------
        Test_Status=True
        if PXIe_4303_Status==0:
            i=0
            for i in range(len(CurrentOutputValue)):
                MyTestResult.Test_Numeric_Results[i]=average[i]
                Test_Status=Test_Status and SelfTest_CF.Test_Numeric_Test(CurrentOutputValue[i],MyTestResult.Test_Numeric_Results[i],5)
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

        # #------------------------------ AO Channels Second Series of Test --------------------------------
        # response = daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-6738 Task"))
        # raise_if_error_daqmx(response)
        # task = response.task
        # i=0
        # CurrentOutputValue =[]
        # MeasuredValue = []
        # for i in range(len(PXIe_6738_Channels_Second_Test)):
        #     CurrentOutputValue.append((float) (Minimal_Value+i*Voltage_Increment))
        #     MeasuredValue.append(9999.9)
        #     i=i+1

        # MyTestResult=SelfTest_CF.Test_Result()
        # MyTestResult.CustomInit('PXIe-6738: check Second Series of Channels.','Fail',len(PXIe_6738_Channels_Second_Test),MeasuredValue, CurrentOutputValue,Create_Test_Module_Description_String(PXIe_6738_Channels_Second_Test, CurrentOutputValue, PXIe_4303_Channels_Second_Test),str(datetime.datetime.now()))
        
        # raise_if_error_daqmx(
        #     daqmx_client.CreateAOVoltageChan(
        #         nidaqmx_types.CreateAOVoltageChanRequest(
        #             task=task,
        #             physical_channel=Create_Channels_String(PXIe_6738_Device,PXIe_6738_Channels_Second_Test),
        #             min_val=-10.0,
        #             max_val=10.0,
        #             units=nidaqmx_types.VOLTAGE_UNITS2_VOLTS,
        #         )
        #     )
        # )

        # raise_if_error_daqmx(daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task)))

        # raise_if_error_daqmx(
        #     daqmx_client.WriteAnalogF64(
        #         nidaqmx_types.WriteAnalogF64Request(
        #             task=task,
        #             num_samps_per_chan=1,
        #             data_layout=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,
        #             write_array=CurrentOutputValue,
        #             timeout=10.0,
        #         )
        #     )
        # )

        # #----------------------------------------------- PXIe-4303 Acquisition  ------------------------------------------------
        # PXIe_4303_Status, Measurements, average=PXIe_4303_Operations(gRPC_channel, PXIe_4303_Device, PXIe_4303_Channels_Second_Test)
        # #-----------------------------------------------------------------------------------------------------------------------
        # Test_Status=True
        # if PXIe_4303_Status==0:
        #     i=0
        #     for i in range(len(CurrentOutputValue)):
        #         MyTestResult.Test_Numeric_Results[i]=average[i]
        #         Test_Status=Test_Status and SelfTest_CF.Test_Numeric_Test(CurrentOutputValue[i],MyTestResult.Test_Numeric_Results[i],5)
        #     if Test_Status==True:
        #         MyTestResult.Test_PassFail_Status='Pass'
        #     else:
        #         MyTestResult.Test_PassFail_Status='Fail'
        # else:
        #     MyTestResult.Test_PassFail_Status='Fail'
        # Tests_Result_list.append(MyTestResult)
        # del MyTestResult     

        # if task:
        #     daqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=task))
        #     daqmx_client.ClearTask(nidaqmx_types.ClearTaskRequest(task=task))

    except:
       #print(f"PXIe-6738 Exception")
       print(f'{"":25}\tERROR\t{"PXIe-6738 Exception.":60}')    
    
    finally:
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    return My_Module_Result 

