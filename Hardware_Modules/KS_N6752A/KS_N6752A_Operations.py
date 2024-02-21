r"""Provides some N6752A features

"""
import sys
import os
import pyvisa
import SelfTest_CF
import datetime
import time

CWD=os.getcwd()
sys.path.append(CWD)

rm=None
PS_KS_N6700=None

def KS_N6752A_Configure_EnableOutput(N6700_Chassis_IP, N6752A_Channel, Voltage_Setpoint, Current_Level):
    r"""This function configures the N6752A module to requested voltage and maximum current and enables the output.

    """
  
    MyTestResult=SelfTest_CF.Test_Result()
    MyTestResult.CustomInit('Keysight N6752A Channel '+str(N6752A_Channel),'Fail',1,[-9999.99],[Voltage_Setpoint],"This test configures N6752A Channel "+str(N6752A_Channel)+" and enables output.",str(datetime.datetime.now()))
    
    try:    
        #Open a session to the N6700 chassis:
        rm = pyvisa.ResourceManager()
        VISA_ResourceName = "TCPIP0::"+N6700_Chassis_IP+"::5025::SOCKET"
        #VISA_ResourceName = "TCPIP0::"+N6700_Chassis_IP+"::INSTR"
        PS_KS_N6700 = rm.open_resource(VISA_ResourceName, read_termination='\n',write_termination='\n')
        PS_KS_N6700.timeout = 250
            
        #Configure Output voltage
        PS_KS_N6700.write("VOLT "+str(Voltage_Setpoint)+", @"+str(N6752A_Channel))
        #Set overvoltage level
        PS_KS_N6700.write("VOLT:PROT:LEV "+str(Voltage_Setpoint*1.1)+", @"+str(N6752A_Channel))
        #Set current level
        PS_KS_N6700.write("CURR "+str(Current_Level)+", @"+str(N6752A_Channel))
        #Turn on over current protection
        PS_KS_N6700.write("CURR:PROT:STAT ON, @"+str(N6752A_Channel))
        #Turn the output ON
        PS_KS_N6700.write("OUTP ON, @"+str(N6752A_Channel))
        #Wait for previous command to complete
        OPC_Answer=PS_KS_N6700.query("*OPC?")
        #Measure the voltage
        Measurement=PS_KS_N6700.query("MEAS:VOLT? @"+str(N6752A_Channel)) 
        MyTestResult.Test_Numeric_Results[0]=float(Measurement)
        
        #Perform comparison between setpoint and actual measurement with 5% tolerance
        Test_Status=SelfTest_CF.Test_Numeric_Test(Voltage_Setpoint,MyTestResult.Test_Numeric_Results[0],5)
        if Test_Status==True:
            MyTestResult.Test_PassFail_Status='Pass'
        else:    
            MyTestResult.Test_PassFail_Status='Fail'
    except:
        PS_KS_N6700=None  
        print(f'{"":25}\tERROR\t{"KS N6752A Exception.":60}')   

    return(MyTestResult,PS_KS_N6700)

def KS_N6752A_DisableOutput(PS_KS_N6700,N6752A_Channel):
    r"""This function disables the N6752A module output.

    """
     #Turn the output OFF
    PS_KS_N6700.write("OUTP OFF, @"+str(N6752A_Channel))
    #Close Connection
    PS_KS_N6700.close()

    return