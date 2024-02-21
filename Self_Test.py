import os
import sys
import grpc
import SelfTest_CF
import SSH_gRPC_Server

CWD=os.getcwd()
#print(f"CWD:{str(CWD)}")

#File path to serialized JSON results
JSON_TEST_FILE_JSONPICKLE = os.path.join(CWD,'Tests_data_JSONPICKLE.json')
JSON_TEST_FILE_JSON_DUMPS = os.path.join(CWD,'Tests_data_JSON_DUMPS.json')
REPORT_FILE_PATH=os.path.join(CWD,'Report.txt')

sys.path.append(os.path.join(CWD,'gRPC_Client','python_sourcefile'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nislsc'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nifpga'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nidaqmx'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','nidcpower'))
sys.path.append(os.path.join(CWD,'Hardware_Modules','KS_N6752A'))

#from SSH_gRPC_Server import Start_gRPC_Server
from SLSC_Operations import SLSC_Operations
from FPGA_RMIO_Operations import FPGA_RMIO_Operations
from FPGA_RDIO_Operations import FPGA_RDIO_Operations
from PXIe_6738_Operations import PXIe_6738_Operations
from PXIe_4322_Operations import PXIe_4322_Operations
from PXIe_4136_Operations import PXIe_4136_Operations

#gRPC Server
ServerIP="192.168.2.34"
ServerPort = 31763
gRPC_channel=None
gRPC_ServerMachine_UserName = 'admin'
gRPC_ServerMachine_Password = ''


#SLSC Chassis
#SLSC_Chassis_Name = "SLSC_XXXXXXXX"
SLSC_Chassis_Name = "SLSC-12001-0310592E"

#FPGA RMIO
RMIO_Bitfile_Path = "//home//admin//FPGA_Bitfiles//PXIe7847R_SelfTest.lvbitx"
RMIO_Bitfile_Signature = "DC163AC6287FBFB65DEEBBBE683470C3"
RMIO_FPGA_ResourceName = "PXI1Slot3"
#FPGA RDIO
RDIO_Bitfile_Path = "//home//admin//FPGA_Bitfiles//PXIe7820R_SelfTest.lvbitx"
RDIO_Bitfile_Signature = "C8C05D6D335094892D20B78090AF3087"
RDIO_FPGA_ResourceName = "PXI1Slot2"

#Analog Output Boards
PXIe_6738_Device = "PXI1Slot8"
PXIe_4322_Device = "PXI1Slot9"

#Analog Input Boards
PXIe_4303_Device = "PXI1Slot10"

#Keysight PowerSupply
N6700_Chassis_IP="192.168.2.75" 
N6752A_Channel_First=1
N6752A_Channel_Second=2

#DC-Power
DCPower_ResourceName_1 = "PXI1Slot12"
DCPower_ResourceName_2 = "PXI1Slot15"
DCPower_Init_Options = "Simulate=1,DriverSetup=Model:4136;BoardType:PXIe"
DCPowerChannels = "0"
DCPower_ResourceName_1_PXIe_4303_Channels = [30]
DCPower_ResourceName_2_PXIe_4303_Channels = [31]

#SelfTest_CF.My_Tests_Result_list=[]
SelfTest_CF.My_Modules_Results=[]

#**********************************************  Start gRPC Server ********************************************
SelfTest_CF.Display_Debug_Info('START gRPC Server')
SSH_gRPC_Server.Start_gRPC_Server(ServerIP, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password)


SelfTest_CF.Display_Debug_Info('SELF-TEST START')
#*******************************************  Instance gRPC Channel ********************************************
try:
    gRPC_channel = grpc.insecure_channel(f"{ServerIP}:{ServerPort}")
    grpc.channel_ready_future(gRPC_channel).result(timeout=3.0)
except grpc.FutureTimeoutError:
    SelfTest_CF.Display_Debug_Info('Error, tinmeout: unable to connecto to gRPC Server.')
else:
    #************************************************** Synthetic Data *********************************************
    # SelfTest_CF.Display_Debug_Info('Syn 0 Test Module: started.')
    # SelfTest_CF.My_Modules_Results.append(SelfTest_CF.Initiate_List(12,'Syn  0'))
    # SelfTest_CF.Display_Debug_Info('Syn 0 Test Module: completed.')

    # SelfTest_CF.Display_Debug_Info('Syn 1 Test Module: started.')
    # SelfTest_CF.My_Modules_Results.append(SelfTest_CF.Initiate_List(3,'Syn  1'))
    # SelfTest_CF.Display_Debug_Info('Syn 1 Test Module: completed.')

    #****************************************************** SLSC ****************************************************
    # SelfTest_CF.Display_Debug_Info('SLSC-12202 Test Module: started.')
    # SelfTest_CF.My_Modules_Results.append(SLSC_Operations(SLSC_Chassis_Name))
    # SelfTest_CF.Display_Debug_Info('SLSC-12202Test Module: completed.')

    #**************************************************** FPGA RMIO *************************************************
    SelfTest_CF.Display_Debug_Info('FPGA RMIO Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(FPGA_RMIO_Operations(gRPC_channel, RMIO_FPGA_ResourceName, RMIO_Bitfile_Path, RMIO_Bitfile_Signature))
    SelfTest_CF.Display_Debug_Info('FPGA RMIO Module: completed.')

    # #**************************************************** FPGA RDIO *************************************************
    SelfTest_CF.Display_Debug_Info('FPGA RDIO Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(FPGA_RDIO_Operations(gRPC_channel, RDIO_FPGA_ResourceName, RDIO_Bitfile_Path, RDIO_Bitfile_Signature))
    SelfTest_CF.Display_Debug_Info('FPGA RDIO Module: completed.')

    # #**********************************************  Analog Outputs Boards ******************************************
    SelfTest_CF.Display_Debug_Info('PXIe-6738 Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(PXIe_6738_Operations(gRPC_channel, PXIe_6738_Device, PXIe_4303_Device))
    SelfTest_CF.Display_Debug_Info('PXIe-6738 Test Module: completed.')

    SelfTest_CF.Display_Debug_Info('PXIe-4322 Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(PXIe_4322_Operations(gRPC_channel, PXIe_4322_Device, PXIe_4303_Device))
    SelfTest_CF.Display_Debug_Info('PXIe-4322 Test Module: completed.')

    #****************************************************  DC Power  *************************************************
    SelfTest_CF.Display_Debug_Info('PXIe-4136_1 Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(PXIe_4136_Operations(gRPC_channel, DCPower_ResourceName_1, DCPower_Init_Options, DCPowerChannels, N6700_Chassis_IP, N6752A_Channel_First))
    SelfTest_CF.Display_Debug_Info('PXIe-4136_1 Test Module: completed.')

    SelfTest_CF.Display_Debug_Info('PXIe-4136_2 Test Module: started.')
    SelfTest_CF.My_Modules_Results.append(PXIe_4136_Operations(gRPC_channel, DCPower_ResourceName_2, DCPower_Init_Options, DCPowerChannels, N6700_Chassis_IP, N6752A_Channel_Second))
    SelfTest_CF.Display_Debug_Info('PXIe-4136_2 Test Module: completed.')
        
    
    #*******************************************  Close gRPC Channel ********************************************
    if gRPC_channel!=None:
        gRPC_channel.close()

#**********************************************  Stop gRPC Server ********************************************
SelfTest_CF.Display_Debug_Info('STOP gRPC Server')
SSH_gRPC_Server.Stop_gRPC_Server(ServerIP, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password)

SelfTest_CF.Display_Debug_Info('SELF-TEST END')
#----------------------------------------  Tests Execution Completed  -------------------------------------------

#We compute the Global Pass/Fail which is a AND between all individual Tests Result
GlobalPassFail=SelfTest_CF.ComputeGlobalPassFail(SelfTest_CF.My_Modules_Results)

#--------------------------------------------------   Report    --------------------------------------------------
SelfTest_CF.Log_Test_Report_TXT(REPORT_FILE_PATH, GlobalPassFail, SelfTest_CF.My_Modules_Results, True, True, True)

print(f"******************************************* TEST DATA LOGGING ***************************************************")
#JSON Serialization/Deserialization
#---- Serialization
# print(f'{"jsonpickle approach: NB Modules logged to file:":36}\t{len(SelfTest_CF.My_Modules_Results)}')
# SelfTest_CF.json_serialize(SelfTest_CF.My_Modules_Results, JSON_TEST_FILE_JSONPICKLE, "jsonpickle")
print(f'{"json.dumps approach: NB Modules logged to file:":36}\t{len(SelfTest_CF.My_Modules_Results)}')
SelfTest_CF.json_serialize(SelfTest_CF.My_Modules_Results, JSON_TEST_FILE_JSON_DUMPS, "json.dumps")

# print(f"******************************************** DATA RETRIEVING ***************************************************")
# #---- Deserialization
# SelfTest_CF.My_TestResult_fromFile=SelfTest_CF.json_load_file(JSON_TEST_FILE_JSONPICKLE, "jsonpickle")
# print(f'{"jsonpickle approach: NB Modules read back from file:":36}\t{len(SelfTest_CF.My_TestResult_fromFile)}')
# SelfTest_CF.My_TestResult_fromFile=SelfTest_CF.json_load_file(JSON_TEST_FILE_JSON_DUMPS, "json.load")
# print(f'{"json.load approach: NB Modules read back from file:":36}\t{len(SelfTest_CF.My_TestResult_fromFile)}')
print(f"************************************************* END **********************************************************")
