r"""Perform finite multipoint acquisition; print the number of points read and average value.
"""  # noqa: W505

import sys
#sys.path.append('/home/admin/grpc-device/gRPC_Client/python_sourcefile')
sys.path.append('C:\\git\\HIL_BMS_Tester_Self_Test\\gRPC_Client\\python_sourcefile')

import time

import grpc
#import matplotlib.pyplot as plt
import nidmm_pb2 as nidmm_types
import nidmm_pb2_grpc as grpc_nidmm
import numpy as np

vi=None
NB_Samples = 100
Status = 0
nidmm_client = None
#channel=None

def check_for_error(vi, status):
    """Raise an exception if the status indicates an error."""
    if status != 0:
        error_message_response = nidmm_client.ErrorMessage(
            nidmm_types.ErrorMessageRequest(vi=vi, error_code=status)
        )
        raise Exception(error_message_response.error_message)
    return status

def DMM_Configure_acquisition(gRPC_channel, DMM_ResourceName, DMM_Init_Options, DMM_MEASUREMENT_TYPE):

    SESSION_NAME = "NI-DMM-Session"
    # parameters
    MAX_PTS_TO_READ = 1000
    RESOLUTION = 5.5
    if (DMM_MEASUREMENT_TYPE == "DC_VOLTS"):
        MEASUREMENT_TYPE = nidmm_types.Function.FUNCTION_NIDMM_VAL_DC_VOLTS
        CONFIG_RANGE = 10.0
    elif (DMM_MEASUREMENT_TYPE == "2_WIRE_RES"):
        MEASUREMENT_TYPE = nidmm_types.Function.FUNCTION_NIDMM_VAL_2_WIRE_RES
        CONFIG_RANGE = 100.0
    else:
        MEASUREMENT_TYPE = nidmm_types.Function.FUNCTION_UNSPECIFIED
        CONFIG_RANGE = -1.0
    POWERLINE_FREQ = nidmm_types.PowerLineFrequencies.POWER_LINE_FREQUENCIES_NIDMM_VAL_60_HERTZ

    def check_for_initialization_error(response):
        """Raise an exception if an error was returned from Initialize."""
        if response.status < 0:
            raise RuntimeError(f"Error: {response.error_message or response.status}")
        if response.status > 0:
            sys.stderr.write(f"Warning: {response.error_message or response.status}\n")

    # Create the communication channel for the remote host and create connections to the NI-DMM and
    # session services.
    #channel = grpc.insecure_channel(f"{server_address}:{server_port}")
    nidmm_client = grpc_nidmm.NiDmmStub(gRPC_channel)

    try:
        #Fake Wait to avoid error:
        time.sleep(0.5)
        # Open session to NI-DMM with options
        init_with_options_response = nidmm_client.InitWithOptions(nidmm_types.InitWithOptionsRequest(session_name=SESSION_NAME, resource_name=DMM_ResourceName, id_query=False, option_string=DMM_Init_Options))
        vi = init_with_options_response.vi
        Status=check_for_initialization_error(init_with_options_response)

        # Configure measurement
        config_measurement_response = nidmm_client.ConfigureMeasurementDigits(nidmm_types.ConfigureMeasurementDigitsRequest(vi=vi,measurement_function=MEASUREMENT_TYPE,range=CONFIG_RANGE,resolution_digits=RESOLUTION))
        Status=check_for_error(vi, config_measurement_response.status)

        # Configure a multipoint acquisition
        config_multipoint_response = nidmm_client.ConfigureMultiPoint(nidmm_types.ConfigureMultiPointRequest(vi=vi,trigger_count_raw=1,sample_count=NB_Samples,sample_trigger=nidmm_types.SampleTrigger.SAMPLE_TRIGGER_NIDMM_VAL_IMMEDIATE,sample_interval_raw=0.001))
        Status=check_for_error(vi, config_multipoint_response.status)

        # Configure powerline frequency
        config_powlinefreq_response = nidmm_client.ConfigurePowerLineFrequency(nidmm_types.ConfigurePowerLineFrequencyRequest(vi=vi, power_line_frequency_hz=POWERLINE_FREQ))
        Status=check_for_error(vi, config_powlinefreq_response.status)

    # # If NI-DMM API throws an exception, print the error message
    # except grpc.RpcError as rpc_error:
    #     error_message = rpc_error.details()
    #     if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
    #         Status=grpc.StatusCode.UNAVAILABLE
    #     elif rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
    #         Status=grpc.StatusCode.UNIMPLEMENTED
    #     print(f"{error_message}")
    # finally:
    #     #print(f"DMM Configuration completed.")
    #     Status=Status
    except:
        print(f"NI-DMM Exception")   
        Status=Status
    return Status, nidmm_client,vi

def DMM_finite_acquisition(nidmm_client,vi):
    try:
        # Initiate Acquisition
        initiate_acquisition_response = nidmm_client.Initiate(nidmm_types.InitiateRequest(vi=vi))
        Status=check_for_error(vi, initiate_acquisition_response.status)

        # Fetch data
        fetch_multipoints_response = nidmm_client.FetchMultiPoint(nidmm_types.FetchMultiPointRequest(vi=vi, maximum_time=-1, array_size=NB_Samples))
        Status=check_for_error(vi, fetch_multipoints_response.status)
        num_pts_read = fetch_multipoints_response.actual_number_of_points
        measurements = np.array(fetch_multipoints_response.reading_array)

        # retain data to 4 decimals
        #measurements = np.floor(measurements * 10000) / 10000.0
        average =  np.average(measurements)

            # If NI-DMM API throws an exception, print the error message
    # except grpc.RpcError as rpc_error:
    #     error_message = rpc_error.details()
    #     if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
    #         Status=grpc.StatusCode.UNAVAILABLE
    #     elif rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
    #         Status=grpc.StatusCode.UNIMPLEMENTED
    #     print(f"{error_message}")
    except :
        print(f"Exception")    
    finally:
        #print(f'DMM Acquisition completed.')
        Status=Status
    return Status, measurements,average

def DMM_Close(nidmm_client,vi):
    if vi.id != 0:
        # Close NI-DMM session
        close_session_response = nidmm_client.Close(nidmm_types.CloseRequest(vi=vi))
        Status=check_for_error(vi, close_session_response.status)
        #channel.close()
    return Status