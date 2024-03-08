r"""PXIe-6738 DI Test Module."""

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

DI_daqmx_client=None
Measurements=[]
Error=0

def PXIe_6738_DI_Operations(gRPC_channel, PXIe_6738_Device, PXIe_6738_DI_Channels):
    
   
    # Create a gRPC channel + client.
    DI_daqmx_client = grpc_nidaqmx.NiDAQmxStub(gRPC_channel)
    task_DI = None
    def raise_if_error_daqmx(response):
        """Raise an exception if an error was returned."""
        if response.status != 0:
            response = DI_daqmx_client.GetErrorString(
                nidaqmx_types.GetErrorStringRequest(error_code=response.status)
            )
            raise Exception(f"Error: {response.error_string}")
    try:
        response = DI_daqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-6738 DI Task"))
        raise_if_error_daqmx(response)
        task_DI = response.task
        LINES=PXIe_6738_Device + "/"+PXIe_6738_DI_Channels
        response=DI_daqmx_client.CreateDIChan(
                nidaqmx_types.CreateDIChanRequest(
                    task=task_DI, lines=LINES, line_grouping=nidaqmx_types.LINE_GROUPING_CHAN_FOR_ALL_LINES
                )
            )
        raise_if_error_daqmx(response)
        raise_if_error_daqmx(DI_daqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=task_DI)))

        response = DI_daqmx_client.ReadDigitalU32(nidaqmx_types.ReadDigitalU32Request(task=task_DI,num_samps_per_chan=1,array_size_in_samps=1,fill_mode=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,timeout=10.0))


        if task_DI:
            DI_daqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=task_DI))
            DI_daqmx_client.ClearTask(nidaqmx_types.ClearTaskRequest(task=task_DI))
            Measurements.extend(response.read_array)
            Error=0
        else:
            Error=-2

    except :
       #print(f"PXIe-6738 Exception")
       print(f'{"":25}\tERROR\t{"PXIe-6738 DI Exception.":60}')
       Error=-1           
    return Error, Measurements  

