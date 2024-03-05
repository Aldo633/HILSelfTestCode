r"""Provides some N6752A features

"""
import sys
import os
import socket
import SelfTest_CF
import datetime
import time

CWD=os.getcwd()
sys.path.append(CWD)

PS_KS_N6700_Socket=None
termination_char='\n'
timeout=1.0

def FormatCommand(Command_String):
    Command_With_termination=Command_String+termination_char
    Command=Command_With_termination.encode()
    return Command

def KS_N6752A_Configure_EnableOutput(N6700_Chassis_IP, N6752A_Channel, Voltage_Setpoint, Current_Level):
    r"""This function configures the N6752A module to requested voltage and maximum current and enables the output.

    """
  
    MyTestResult=SelfTest_CF.Test_Result()
    MyTestResult.CustomInit('Keysight N6752A Channel '+str(N6752A_Channel),'Fail',1,[-9999.99],[Voltage_Setpoint],"This test configures N6752A Channel "+str(N6752A_Channel)+" and enables output.",str(datetime.datetime.now()))
    
    # Create a socket
    PS_KS_N6700_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PS_KS_N6700_Socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    try:    
        # Connect to the instrument 
        PS_KS_N6700_Socket.connect((N6700_Chassis_IP, 5025))
      
        #Configure Output voltage
        PS_KS_N6700_Socket.send(FormatCommand("VOLT "+str(Voltage_Setpoint)+", @"+str(N6752A_Channel)))
        #Set overvoltage level
        PS_KS_N6700_Socket.send(FormatCommand("VOLT:PROT:LEV "+str(Voltage_Setpoint*1.1)+", @"+str(N6752A_Channel)))
        #Set current level
        PS_KS_N6700_Socket.send(FormatCommand("CURR "+str(Current_Level)+", @"+str(N6752A_Channel)))
        #Turn on over current protection
        PS_KS_N6700_Socket.send(FormatCommand("CURR:PROT:STAT ON, @"+str(N6752A_Channel)))
        #Turn the output ON
        PS_KS_N6700_Socket.send(FormatCommand("OUTP ON, @"+str(N6752A_Channel)))
        #Wait for previous command to complete
        PS_KS_N6700_Socket.send(FormatCommand("*OPC?"))
        #time.sleep(2)
        OPC_Answer=PS_KS_N6700_Socket.recv(256)
        if OPC_Answer:
            #Measure the voltage
            PS_KS_N6700_Socket.send(FormatCommand("MEAS:VOLT? @"+str(N6752A_Channel))) 
            Measurement=PS_KS_N6700_Socket.recv(256)
            if Measurement:
                MyTestResult.Test_Numeric_Results[0]=float(Measurement)
            else:
                MyTestResult.Test_Numeric_Results[-5000]
        else:
            MyTestResult.Test_Numeric_Results[-5001]
        #Perform comparison between setpoint and actual measurement with 5% tolerance
        Test_Status=SelfTest_CF.Test_Numeric_Test(Voltage_Setpoint,MyTestResult.Test_Numeric_Results[0],5)
        if Test_Status==True:
            MyTestResult.Test_PassFail_Status='Pass'
        else:    
            MyTestResult.Test_PassFail_Status='Fail'
    except PS_KS_N6700_Socket.timeout:
        #PS_KS_N6700=None  
        print(f'{"":25}\tERROR\t{"KS N6752A Socket Timeout Exception.":60}')   
    except :
        print(f'{"":25}\tERROR\t{"KS N6752A Socket Exception.":60}')   
 
    return(MyTestResult,PS_KS_N6700_Socket)

def KS_N6752A_DisableOutput(PS_KS_N6700_Socket,N6752A_Channel):
    r"""This function disables the N6752A module output.

    """
    #  #Turn the output OFF
    PS_KS_N6700_Socket.send(FormatCommand("OUTP OFF, @"+str(N6752A_Channel)))
    PS_KS_N6700_Socket.close()


    return