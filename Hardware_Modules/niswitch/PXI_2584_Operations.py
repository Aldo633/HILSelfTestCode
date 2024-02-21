r"""Scan a series of channels on a module using software scanning.

The gRPC API is built from the C API. NI-SWITCH documentation is installed with the driver at:
  C:\Program Files (x86)\IVI Foundation\IVI\Drivers\niSwitch\Documentation\English\SWITCH.chm

A version of this .chm is available online at:
  https://zone.ni.com/reference/en-XX/help/375472H-01/

Getting Started:

For instructions on how to use protoc to generate gRPC client interfaces, see our "Creating a gRPC
Client" wiki page:
  https://github.com/ni/grpc-device/wiki/Creating-a-gRPC-Client

Refer to the NI-SWITCH Help to determine if your module supports scanning, the scan list syntax,
valid channel names and valid resource names.

Refer to the NI-SWITCH gRPC Wiki for the latest C Function Reference:
  https://github.com/ni/grpc-device/wiki/NI-SWITCH-C-Function-Reference

Running from command line:

Server machine's IP address and port numbercan be passed as separate command line arguments.
  > python software-scanning.py <server_address> <port_number>
If they are not passed in as command line arguments, then by default the server address will be
"localhost:31763".
To successfully run this example, the resource name, topology, and scan list must be hard coded in
this file.
"""

import sys
import time
import os
import grpc

sys.path.append('C:\\git\\HIL_BMS_Tester_Self_Test\\gRPC_Client\\python_sourcefile')

import niswitch_pb2 as niswitch_types
import niswitch_pb2_grpc as grpc_niswitch

TOPOLOGY_STRING = "2584/2-Wire 6x1 Mux"
SIMULATION = True
SESSION_NAME = "NI-Switch-Session-1"
Status=None

def PXI_2584_Connect(gRPC_channel, PXI2584_ResourceName, channel1, channel2):
    #channel = grpc.insecure_channel(f"{ServerIP}:{ServerPort}")
    niswitch_client = grpc_niswitch.NiSwitchStub(gRPC_channel)

    def check_for_error(vi, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = niswitch_client.ErrorMessage(niswitch_types.ErrorMessageRequest(vi=vi, error_code=status))
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
            resource_name=PXI2584_ResourceName,
            topology=TOPOLOGY_STRING,
            simulate=SIMULATION,
            reset_device=True,
        )
    )
    try:
        vi = init_with_topology_response.vi
        Status=check_for_initialization_error(init_with_topology_response)

        #Connect channel1 to channel2
        Status=check_for_error(vi, (niswitch_client.Connect(niswitch_types.ConnectRequest(vi=vi,channel1=channel1,channel2=channel2))).status)
            
        # If NI-SWITCH API throws an exception, return the error code
    # except grpc.RpcError as rpc_error:
    #     error_message = rpc_error.details()
    #     if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
    #         error_message = f"Failed to connect to server on {ServerIP}:{ServerPort}"
    #         Status=grpc.StatusCode.UNAVAILABLE
    #     elif rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
    #         error_message = ("The operation is not implemented or is not supported/enabled in this service")
    #     print(f"{error_message}")
    #     Status=rpc_error.code()
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
        if "vi" in vars() and vi.id != 0:
            # close the session.
            niswitch_client.Close(niswitch_types.CloseRequest(vi=vi))
        #channel.close()
    return Status

def PXI_2584_DisconnectAll(gRPC_channel,PXI2584_ResourceName):
    #channel = grpc.insecure_channel(f"{ServerIP}:{ServerPort}")
    niswitch_client = grpc_niswitch.NiSwitchStub(gRPC_channel)

    def check_for_error(vi, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = niswitch_client.ErrorMessage(niswitch_types.ErrorMessageRequest(vi=vi, error_code=status))
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
        #Open session to NI-SWITCH and set topology.
        init_with_topology_response = niswitch_client.InitWithTopology(
            niswitch_types.InitWithTopologyRequest(
                session_name=SESSION_NAME,
                resource_name=PXI2584_ResourceName,
                topology=TOPOLOGY_STRING,
                simulate=SIMULATION,
                reset_device=True,
            )
        )

        vi = init_with_topology_response.vi
        Status=check_for_initialization_error(init_with_topology_response)

        #Disconnect ALL
        Status=check_for_error(vi, (niswitch_client.DisconnectAll(niswitch_types.DisconnectAllRequest(vi=vi))).status)
        
    # If NI-SWITCH API throws an exception, return the error code
    # except grpc.RpcError as rpc_error:
    #     error_message = rpc_error.details()
    #     if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
    #         error_message = f"Failed to connect to server on {ServerIP}:{ServerPort}"
    #         Status=grpc.StatusCode.UNAVAILABLE
    #     elif rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
    #         error_message = ("The operation is not implemented or is not supported/enabled in this service")
    #     print(f"{error_message}")
    #     Status=rpc_error.code()
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
        if "vi" in vars() and vi.id != 0:
            # close the session.
            niswitch_client.Close(niswitch_types.CloseRequest(vi=vi))
        #channel.close()
    return Status
