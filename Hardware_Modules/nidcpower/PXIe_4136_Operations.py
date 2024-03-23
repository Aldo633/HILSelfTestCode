r"""PXIe-4136 Test Module."""
TEST_MODULE_NAME = 'PXIe-4136 '

from KS_N6752A_Operations import KS_N6752A_Configure_EnableOutput, KS_N6752A_DisableOutput

Measurements=[]
grpc_nidmm=None
vi_nidmm=None
dmm_Status=None
average=None

Voltage_Setpoint=10
Current_Level=0.05

PS_KS_N6700=None

# def Create_Channels_String(Device_Resource_Name, Channels):
#     """This function prepares the NI-DAQmx channels string."""
#     i=0
#     Channels_String=''
#     for i in range(len(Channels)):
#         Channels_String=Channels_String+ Device_Resource_Name + "/ao" + str(Channels[i])
#         if i<len(Channels)-1:
#             Channels_String=Channels_String+","
#         i=i+1
#     return Channels_String

# def Create_Test_Module_Description_String(PXIe_4322_Channels, CurrentOutputValue, PXIe_4303_Channels):
#     """This function returns the Test Module Description String based on the list of Channels passed as argument."""
#     i=0
#     Description_String='This test outputs ['
#     for i in range(len(PXIe_4322_Channels)):
#         Description_String=Description_String+ str(CurrentOutputValue[i])
#         if i <len(PXIe_4322_Channels)-1:
#             Description_String=Description_String+","
#         i=i+1
#     Description_String=Description_String+'] Volts on channels ['
#     i=0
#     for i in range(len(PXIe_4322_Channels)):
#         Description_String=Description_String+ str(PXIe_4322_Channels[i])
#         if i <len(PXIe_4322_Channels)-1:
#             Description_String=Description_String+","
#         i=i+1
#     Description_String=Description_String+'] of PXIe-4322 and measures actual value using following PXIe-4303 channels: ['
#     i=0
#     for i in range(len(PXIe_4322_Channels)):
#         Description_String=Description_String+ str(PXIe_4303_Channels[i])
#         if i <len(PXIe_4322_Channels)-1:
#             Description_String=Description_String+","
#         i=i+1

#     Description_String=Description_String+'].'
#     return Description_String

def PXIe_4136_Operations(gRPC_channel, DCPower_ResourceName, DCPower_Init_Options, DCPowerChannels, N6700_Chassis_IP, N6752A_Channel):
    """Outputs a DC Voltage to an Analog Output of SMU PXIe-4136."""
    import math
    import sys
    import time
    import os
    import datetime
    import grpc


    import SelfTest_CF

    
    #from PXIe_4303_Operations import PXIe_4303_Operations

    import nidcpower_pb2 as nidcpower_types
    import nidcpower_pb2_grpc as grpc_nidcpower
    import numpy as np

    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = TEST_MODULE_NAME+DCPower_ResourceName+" Keysight PS Channel "+str(N6752A_Channel)
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    SESSION_NAME = "NI-DCPower-Session"

    # Parameters
    VOLTAGE_LEVEL = 9.0
    VOLTAGE_LEVEL_RANGE = 10.0
    CURRENT_LIMIT=0.01
    CURRENT_LEVEL = 0.0005
    CURRENT_LIMIT_RANGE=0.0
    SOURCE_DELAY_SEC=0.1

    def check_for_error(vi, status):
        """Raise an exception if the status indicates an error."""
        if status != 0:
            error_message_response = nidcpower_client.ErrorMessage(
                nidcpower_types.ErrorMessageRequest(vi=vi, error_code=status)
            )
            raise Exception(error_message_response.error_message)


    def check_for_initialization_error(response):
        """Raise an exception if an error was returned from Initialize."""
        if response.status < 0:
            raise RuntimeError(f"Error: {response.error_message or response.status}")
        if response.status > 0:
            sys.stderr.write(f"Warning: {response.error_message or response.status}\n")


    # Create the communication channel for the remote host and create connections to the NI-DCPower and
    # session services.
    nidcpower_client = grpc_nidcpower.NiDCPowerStub(gRPC_channel)

    try:
        #------------------------------ Configure SMU Output  -------------------------------
        # Initialize the session.
        initialize_with_channels_response = nidcpower_client.InitializeWithChannels(
            nidcpower_types.InitializeWithChannelsRequest(
                session_name=SESSION_NAME,
                resource_name=DCPower_ResourceName,
                channels=DCPowerChannels,
                reset=False,
                option_string=DCPower_Init_Options,
            )
        )
        vi = initialize_with_channels_response.vi
        check_for_initialization_error(initialize_with_channels_response)

        # Configure source mode.
        configure_source_mode = nidcpower_client.ConfigureSourceMode(
            nidcpower_types.ConfigureSourceModeRequest(
                vi=vi,
                source_mode=nidcpower_types.SourceMode.SOURCE_MODE_NIDCPOWER_VAL_SINGLE_POINT,
            )
        )
        check_for_error(vi, configure_source_mode.status)

        # Configure output function.
        configure_output_function = nidcpower_client.ConfigureOutputFunction(
            nidcpower_types.ConfigureOutputFunctionRequest(
                vi=vi,
                channel_name = DCPowerChannels,
                function = nidcpower_types.OutputFunction.OUTPUT_FUNCTION_NIDCPOWER_VAL_DC_CURRENT,
            )
        )
        check_for_error(vi, configure_output_function.status)

        # Configure voltage limit.
        configure_voltage_limit = nidcpower_client.ConfigureVoltageLimit(
            nidcpower_types.ConfigureVoltageLimitRequest(
                vi=vi,
                channel_name="0",
                limit=VOLTAGE_LEVEL_RANGE,
            )
        )
        check_for_error(vi, configure_voltage_limit.status)

        # # Configure voltage limit range.
        # configure_voltage_limit_range = nidcpower_client.ConfigureVoltageLimitRange(
        #     nidcpower_types.ConfigureVoltageLimitRangeRequest(
        #         vi=vi,
        #         channel_name="0",
        #         limit=VOLTAGE_LEVEL_RANGE,
        #     )
        # )
        # check_for_error(vi, configure_voltage_limit.status)

  
        # Configure current level.
        # configure_current_level = nidcpower_client.ConfigureCurrentLevel(
        #     nidcpower_types.ConfigureCurrentLevelRequest(
        #         vi=vi,
        #         channel_name=DCPowerChannels,
        #         level=0.0,
        #     )
        # )
        # check_for_error(vi, configure_current_level.status)

        # # Configure current limit.
        configure_current_limit = nidcpower_client.ConfigureCurrentLimit(
            nidcpower_types.ConfigureCurrentLimitRequest(
                vi=vi,
                channel_name=DCPowerChannels,
                behavior=nidcpower_types.CurrentLimitBehavior.CURRENT_LIMIT_BEHAVIOR_NIDCPOWER_VAL_CURRENT_REGULATE,
                limit=CURRENT_LIMIT,
            )
        )
        check_for_error(vi, configure_current_limit.status)



        # # Configure voltage level range.
        # configure_voltage_level_range = nidcpower_client.ConfigureVoltageLevelRange(
        #     nidcpower_types.ConfigureVoltageLevelRangeRequest(
        #         vi=vi,
        #         channel_name=DCPowerChannels,
        #         range=VOLTAGE_LEVEL_RANGE,
        #     )
        # )
        # check_for_error(vi, configure_voltage_level_range.status)

        # # Configure current limit range.
        # configure_current_limit_range = nidcpower_client.ConfigureCurrentLimitRange(
        #     nidcpower_types.ConfigureCurrentLimitRangeRequest(
        #         vi=vi,
        #         channel_name=DCPowerChannels,
        #         range=CURRENT_LIMIT_RANGE,
        #     )
        # )
        # check_for_error(vi, configure_current_limit_range.status)

        # #Configure Source Delay
        # set_source_delay = nidcpower_client.SetAttributeViReal64(
        #     nidcpower_types.SetAttributeViReal64Request(
        #         vi=vi,
        #         channel_name=DCPowerChannels,
        #         attribute_id=nidcpower_types.NiDCPowerAttribute.NIDCPOWER_ATTRIBUTE_SOURCE_DELAY,
        #         attribute_value_raw=SOURCE_DELAY_SEC,
        #     )
        # )
        # check_for_error(vi, set_source_delay.status)

        #Configures and Enables Keysight
        MyTestResult,PS_KS_N6700=KS_N6752A_Configure_EnableOutput(N6700_Chassis_IP, N6752A_Channel, Voltage_Setpoint, Current_Level)
        Tests_Result_list.append(MyTestResult)
        del MyTestResult

        if Tests_Result_list[0].Test_PassFail_Status !="Fail":
            # initiate the session.
            initiate_response = nidcpower_client.Initiate(
                nidcpower_types.InitiateRequest(
                    vi=vi,

                )
            )
            check_for_error(vi, initiate_response.status)

            # Wait for Event.
            Wait_for_event_with_Channels = nidcpower_client.WaitForEventWithChannels(
                nidcpower_types.WaitForEventWithChannelsRequest(
                    vi=vi,
                    channel_name=DCPowerChannels,
                    event_id=nidcpower_types.ExportSignal.EXPORT_SIGNAL_NIDCPOWER_VAL_SOURCE_COMPLETE_EVENT,
                    timeout=5,
                )
            )
            check_for_error(vi,Wait_for_event_with_Channels.status)

            # Measure Multiple
            measure_multiple = nidcpower_client.MeasureMultiple(
                nidcpower_types.MeasureMultipleRequest(
                    vi=vi,
                    channel_name=DCPowerChannels,
                )
            )
            check_for_error(vi,measure_multiple.status)

            # Test with SMU Feedback Channel
            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('PXIe-4136: CH'+DCPowerChannels+ ' with SMU feedback channel','Fail',1,[0],[Voltage_Setpoint],'This test measures actual value on channel ch'+DCPowerChannels+'. Voltage is output by Keysight Power Supply Channel '+str(N6752A_Channel),str(datetime.datetime.now()))
            
            Test_Status=True
            if measure_multiple.status==0:
                i=0
                for i in range(MyTestResult.Test_Number_Of_Measurements):
                    MyTestResult.Test_Numeric_Results[i]=measure_multiple.voltage_measurements[i]
                    Test_Status=Test_Status and SelfTest_CF.Test_Numeric_Test(MyTestResult.Test_Expected_Numeric_Results[i],MyTestResult.Test_Numeric_Results[i],10)
                if Test_Status==True:
                    MyTestResult.Test_PassFail_Status='Pass'
                else:
                    MyTestResult.Test_PassFail_Status='Fail'
            else:
                MyTestResult.Test_PassFail_Status='Fail'
            Tests_Result_list.append(MyTestResult)
            del MyTestResult           
        else:
            # Test with SMU Feedback Channel
            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('PXIe-4136: CH'+DCPowerChannels+ ' with SMU feedback channel','Fail',1,[-9999.99],[Voltage_Setpoint],'This test measures actual value on channel ch'+DCPowerChannels+'. Voltage is output by Keysight Power Supply Channel '+str(N6752A_Channel),str(datetime.datetime.now()))
            MyTestResult.Test_PassFail_Status='Fail'
            Tests_Result_list.append(MyTestResult)
            del MyTestResult    
   
    except :
    #     print(f"NI-DCPOWER Exception")    
        print(f'{"":25}\tERROR\t{"PXIe-4136 Exception.":60}')    
        #PS_KS_N6700=None

    finally:
        #We disable PS output and close session
        if Tests_Result_list[0].Test_PassFail_Status !="Fail":
            KS_N6752A_DisableOutput(PS_KS_N6700,N6752A_Channel)
            PS_KS_N6700=None
         #---------------------- Close NI-DC Power session -----------------------
        if "vi" in vars() and vi.id != 0:
            #Reset
            reset = nidcpower_client.ResetWithChannels(
            nidcpower_types.ResetWithChannelsRequest(
                    vi=vi,
                    channel_name=DCPowerChannels,
                )
            )

            # close the session.
            check_for_error(vi, (nidcpower_client.Close(nidcpower_types.CloseRequest(vi=vi))).status)

        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    return My_Module_Result 
