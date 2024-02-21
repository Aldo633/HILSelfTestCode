r"""PXIe-4303 Acquisition Module."""

def Create_Channels_String(Device_Resource_Name, Channels):
    """This function prepares the NI-DAQmx channels string."""
    i=0
    Channels_String=''
    for i in range(len(Channels)):
        Channels_String=Channels_String+ Device_Resource_Name + "/ai" + str(Channels[i])
        if i<len(Channels)-1:
            Channels_String=Channels_String+","
        i=i+1
    return Channels_String


def PXIe_4303_Operations(gRPC_channel, PXIe_4303_Device, Channels):

    import sys
    import os

    import grpc
    import nidaqmx_pb2 as nidaqmx_types
    import nidaqmx_pb2_grpc as grpc_nidaqmx
    import numpy as np


   # Create a client.
    nidaqmx_client = grpc_nidaqmx.NiDAQmxStub(gRPC_channel)
    ai_task = None
    Status = 0
    NUM_SAMPS_PER_CHAN = 1000


    def raise_if_error(response):
        """Raise an exception if an error was returned."""
        if response.status != 0:
            response = nidaqmx_client.GetErrorString(
                nidaqmx_types.GetErrorStringRequest(error_code=response.status)
            )
            raise Exception(f"Error: {response.error_string}")


    try:
        response = nidaqmx_client.CreateTask(nidaqmx_types.CreateTaskRequest(session_name="My PXIe-4303 Task"))
        raise_if_error(response)
        ai_task = response.task
        raise_if_error(
            nidaqmx_client.CreateAIVoltageChan(
                    nidaqmx_types.CreateAIVoltageChanRequest(
                        task=ai_task,
                        physical_channel=Create_Channels_String(PXIe_4303_Device, Channels),
                        terminal_config=nidaqmx_types.INPUT_TERM_CFG_WITH_DEFAULT_CFG_DEFAULT,
                        min_val=-10.0,
                        max_val=10.0,
                        units=nidaqmx_types.VOLTAGE_UNITS2_VOLTS,
                    )
                )
        )

        raise_if_error(
            nidaqmx_client.CfgSampClkTiming(
                nidaqmx_types.CfgSampClkTimingRequest(
                    task=ai_task,
                    rate=10000.0,
                    active_edge=nidaqmx_types.EDGE1_RISING,
                    sample_mode=nidaqmx_types.ACQUISITION_TYPE_FINITE_SAMPS,
                    samps_per_chan=NUM_SAMPS_PER_CHAN,
                )
            )
        )

        raise_if_error(nidaqmx_client.StartTask(nidaqmx_types.StartTaskRequest(task=ai_task)))

        # Get the number of channels. This may be greater than 1 if the physical_channel
        # parameter is a list or range of channels.
        response = nidaqmx_client.GetTaskAttributeUInt32(
            nidaqmx_types.GetTaskAttributeUInt32Request(
                task=ai_task, attribute=nidaqmx_types.TASK_ATTRIBUTE_NUM_CHANS
            )
        )
        raise_if_error(response)
        number_of_channels = response.value

        response = nidaqmx_client.ReadAnalogF64(
            nidaqmx_types.ReadAnalogF64Request(
                task=ai_task,
                num_samps_per_chan=NUM_SAMPS_PER_CHAN,
                array_size_in_samps=number_of_channels * NUM_SAMPS_PER_CHAN,
                fill_mode=nidaqmx_types.GROUP_BY_GROUP_BY_CHANNEL,
                timeout=10.0,
            )
        )
        raise_if_error(response)
        # print(
        #     f"Acquired {len(response.read_array)} samples",
        #     f"({response.samps_per_chan_read} samples per channel)",
        # )
        measurements=np.array(response.read_array)
        #average=np.full(number_of_channels, 0.0)
        average=[]
        i=0
        for i in range(number_of_channels):
            #average[i]=np.average(measurements[i*NUM_SAMPS_PER_CHAN:((i+1)*NUM_SAMPS_PER_CHAN)-1])
            average.append(np.average(measurements[i*NUM_SAMPS_PER_CHAN:((i+1)*NUM_SAMPS_PER_CHAN)-1]))
            i=i+1
    except:
        print(f'{"":25}\tERROR\t{"PXIe-4303 Exception.":60}') 
        Status=-1
        measurements=np.array(np.nan)
        average=np.nan      
    finally:
        if ai_task:
            nidaqmx_client.StopTask(nidaqmx_types.StopTaskRequest(task=ai_task))
            nidaqmx_client.ClearTask(nidaqmx_types.ClearTaskRequest(task=ai_task))
    return Status, measurements,average