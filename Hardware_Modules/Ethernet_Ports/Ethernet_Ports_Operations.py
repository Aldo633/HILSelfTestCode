r"""Ethernet_Ports Test Module."""

import sys
import os
import SelfTest_CF
import datetime
import time
import paramiko
import csv
import subprocess


Measurements=[]
average=None
USBFolder = os.getcwd()+'/Hardware_Modules/Ethernet_Ports'
NO_OF_USB_PORTS = 1


def extract_string_between_variables(input_string:str, start_variable:str, end_variable:str):
    try:
        # Find the index of the start variable
        start_index = input_string.index(start_variable) + len(start_variable)
        
        # Find the index of the end variable
        end_index = input_string.index(end_variable, start_index)
        
        # Extract the substring between the start and end variables
        result = input_string[start_index:end_index]
        return result
    except ValueError:
        return None

def substring_after(s, delim):
    return s.partition(delim)[2]

class Commands:
    Count_USBEth_Adapters_Command=(USBFolder+'/Count_USB_Devices.sh')
    Get_USBEth_Adapters_Information_Command=(USBFolder+'/Get_USB_Devices_Information.sh')
    Ping_Command=(USBFolder+'/Ping_Interface.sh')

    def __init__(self, retry_time=0):
        self.retry_time = retry_time
        pass

    def Count_USBEth_Adapters(self, host_ip, Machine_UserName, Machine_Password, Vendor_ID, Product_ID):
        i = 0
        while True:
            SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Trying to connect to %s (%i/%i)" % (host_ip, i, self.retry_time))
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
                ssh.connect(host_ip, username=Machine_UserName, password=Machine_Password, port=22)
                break
            except paramiko.AuthenticationException:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Authentication failed when connecting to %s" % host_ip)
                sys.exit(1)
            except paramiko.SSHException:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] SSH Exception. It failed when connecting to %s" % host_ip)
                sys.exit(1)
            except:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i >= self.retry_time:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not connect to %s. Giving up" % host_ip)
                sys.exit(1)

        # Count Number of USB to Ethernet Adapters.
        NB_Adapters=0
        SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Count Number of USB->Ethernet Adapters')
        #Count_Command=self.Count_USBEth_Adapters_Command+" "+str(Vendor_ID)+" "+str(Product_ID)
        Count_Command=self.Count_USBEth_Adapters_Command
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(Count_Command)
        exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
        if exit_code==0:
            for line in ssh_stdout:
                    NB_Adapters= line.strip()
                    SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Number of USB->Ethernet Adapters Detected: '+str(NB_Adapters))
            
        # Close SSH connection
        ssh.close()
        return NB_Adapters

    def Get_USBEth_Adapters_Information(self, host_ip, Machine_UserName, Machine_Password, Vendor_ID,Product_ID,NB_Adapters):
        i = 0
        while True:
            SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Trying to connect to %s (%i/%i)" % (host_ip, i, self.retry_time))
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
                ssh.connect(host_ip, username=Machine_UserName, password=Machine_Password, port=22)
                break
            except paramiko.AuthenticationException:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Authentication failed when connecting to %s" % host_ip)
                sys.exit(1)
            except paramiko.SSHException:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] SSH Exception. It failed when connecting to %s" % host_ip)
                sys.exit(1)
            except:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i >= self.retry_time:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not connect to %s. Giving up" % host_ip)
                sys.exit(1)

        # Get USB to Ethernet Adapters Information.
        SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Get USB->Ethernet Adapters Information')
        #Get_Information_Command=self.Get_USBEth_Adapters_Information_Command+" "+str(Vendor_ID)+" "+str(Product_ID)
        Get_Information_Command=self.Get_USBEth_Adapters_Information_Command
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(Get_Information_Command)
        exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
        if exit_code==0:
                decoded_ssh_stdout=ssh_stdout.read().decode('utf-8')
                # Split the output by newline
                lines = decoded_ssh_stdout.split('\n')
                #print(lines)
                # Extract column names from the first line
                column_names = lines[0].split()
                #SelfTest_CF.Display_Debug_Info('[Ethernet Ports] '+str(column_names))
                # Initialize an empty list to store the data
                Adapters_List = []
                lines.pop()
                for line in lines[1:]:
                           # Process the remaining lines
                            values = line.split()
                            data_dict = {column: value for column, value in zip(column_names, values)}
                            Adapters_List.append(data_dict)
                SelfTest_CF.Display_Debug_Info('[Ethernet Ports] '+str(Adapters_List))              
                                
        # Close SSH connection
        ssh.close()
        return Adapters_List   


    def Get_Eth_Interface_Information(self, host_ip, Machine_UserName, Machine_Password, MAC_Address, Testing):
        if Testing!=True:
            i = 0
            while True:
                SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Trying to connect to %s (%i/%i)" % (host_ip, i, self.retry_time))
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
                    ssh.connect(host_ip, username=Machine_UserName, password=Machine_Password, port=22)
                    break
                except paramiko.AuthenticationException:
                    SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Authentication failed when connecting to %s" % host_ip)
                    sys.exit(1)
                except paramiko.SSHException:
                    SelfTest_CF.Display_Debug_Info("[Ethernet Ports] SSH Exception. It failed when connecting to %s" % host_ip)
                    sys.exit(1)
                except:
                    SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not SSH to %s, waiting for it to start" % host_ip)
                    i += 1
                    time.sleep(2)

                # If we could not connect within time limit
                if i >= self.retry_time:
                    SelfTest_CF.Display_Debug_Info("[Ethernet Ports] Could not connect to %s. Giving up" % host_ip)
                    sys.exit(1)

            SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Get Ethernet Interface Adapter Information')
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ifconfig')
            exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
            EthName=""
            IP_Address=""
            if exit_code==0:
                    decoded_ssh_stdout=ssh_stdout.read().decode('utf-8')
                    #print(decoded_ssh_stdout)
                    while (len(decoded_ssh_stdout)>0):   
                        #We limit search area to current interface:
                        Temp=extract_string_between_variables(decoded_ssh_stdout, "flags=", " collisions")
                        #Search for IP Address
                        Extracted_String=extract_string_between_variables(str(Temp), "inet ", "  netmask")
                        if len(Extracted_String)>0:
                            if MAC_Address==extract_string_between_variables(Temp, "ether ", "  txqueuelen"):
                                #Ethernet Interface Name
                                EthName=decoded_ssh_stdout[:decoded_ssh_stdout.index(":")]
                                #IP Address
                                IP_Address=extract_string_between_variables(str(Temp), "inet ", "  netmask")
                                decoded_ssh_stdout=""
                        decoded_ssh_stdout=substring_after(decoded_ssh_stdout, "\n\n")                         
                                    
            # Close SSH connection
            ssh.close()
        else:
            EthName="eth99"
            IP_Address="192.168.0.50"
        return EthName, IP_Address   

    def Ping_Interface(self, Source_IP, Destimation_IP, NB_Replies):
        SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Ping Ethernet Interface')

        # status = subprocess.call(
        #     ['ping', '-q', '-I',Source_IP,'-c',NB_Replies, Destimation_IP],
        #     stdout=subprocess.DEVNULL)
        
        # Execute the ping command and capture the output
        try:
            result = subprocess.check_output(['ping', '-I', Source_IP, '-c', str(NB_Replies), Destimation_IP], stderr=subprocess.DEVNULL, text=True)
            #print(f"Ping output:\n{result}")
            error=0;
    
        except subprocess.CalledProcessError as e:
            SelfTest_CF.Display_Debug_Info('[Ethernet Ports] Exception during Ping.')
            error=-1
        return error   



def Count_USBEth_Adapters(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID):
    NB_Adapters=0
    MyCommands = Commands()
    NB_Adapters=MyCommands.Count_USBEth_Adapters(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,USB_Adapter_Vendor_ID, USB_Adapter_Product_ID)
    return NB_Adapters

def Get_USBEth_Adapters_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID,NB_Adapters):
    Adapters_List=[]
    MyCommands = Commands()
    Adapters_List=MyCommands.Get_USBEth_Adapters_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,USB_Adapter_Vendor_ID, USB_Adapter_Product_ID,NB_Adapters)
    return Adapters_List

def Get_Eth_Interface_Information(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, MAC_Address, Testing):
    MyCommands = Commands()
    EthName, IP_Address=MyCommands.Get_Eth_Interface_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, MAC_Address, Testing)
    return EthName, IP_Address

def Ping_Interface(Source_IP, Destimation_IP, NB_Replies):
    MyCommands = Commands()
    error=MyCommands.Ping_Interface(Source_IP, Destimation_IP, NB_Replies)
    return error 

def Get_MAC_IP_Addresses(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,Adapters_List,MAP_SN_MAC_ADDRESS_File_Path,Testing):
    try:
        # Read the tab-delimited file
        with open(MAP_SN_MAC_ADDRESS_File_Path, 'r') as file:
            lines = file.readlines()
        

        # Create a list of dictionaries
        SN_MAC_Dict = []

        for line in lines[1:]:
            Serial_Number, MAC_Address = line.strip().split("\t")
            SN_MAC_Dict.append({"Serial_Number": Serial_Number, "MAC_Address": MAC_Address})
                    
   
        Adapters_List_With_MAC=Adapters_List
        
        #Find MAC Addresses Match from SN_MAC
        i=0
        for i in range(len(Adapters_List)):
            target_serial_number = Adapters_List[i]['Serial_Number']
            for record in SN_MAC_Dict:
                if record["Serial_Number"] == target_serial_number:
                    SelfTest_CF.Display_Debug_Info("[Ethernet Ports] MACAddress for SerialNumber {target_serial_number}: {record['MAC_Address']}")
                    #MAC found, we insert it.
                    Adapters_List_With_MAC[i]['MAC_Address']=record['MAC_Address']
                    EthName, IP_Address=Get_Eth_Interface_Information(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, Adapters_List_With_MAC[i]['MAC_Address'], Testing)
                    if EthName !='':
                        Adapters_List_With_MAC[i]['Eth_Name']=EthName
                    if IP_Address !='':
                        Adapters_List_With_MAC[i]['IP_Address']=IP_Address

    except:
        print("Exception!")
    return Adapters_List_With_MAC

def Ethernet_Ports_Operations(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,USB_Adapter_Vendor_ID, USB_Adapter_Product_ID,MAP_SN_MAC_ADDRESS_File_Path, IP_Ping_Source, Testing):
    
    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = "Ethernet Ports"
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    try:
        #Count Number of USB->Adapters
        NB_Adapters_Detected=0
        NB_Adapters_Detected=Count_USBEth_Adapters(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID)


        MyTestResult=SelfTest_CF.Test_Result()
        MyTestResult.CustomInit('Count USB Ethernet Adapters','Fail',1,[0],[NO_OF_USB_PORTS],'This test counts number of USB Ethernet Adapters.',str(datetime.datetime.now()))
      
        MyTestResult.Test_Numeric_Results[0]=int(NB_Adapters_Detected)
        # MyTestResult.Test_Expected_Numeric_Results.append(NO_OF_USB_PORTS)

        if MyTestResult.Test_Numeric_Results[0]!=MyTestResult.Test_Expected_Numeric_Results[0]:
            MyTestResult.Test_PassFail_Status='Fail'
        else:
            MyTestResult.Test_PassFail_Status='Pass'
        Tests_Result_list.append(MyTestResult)
        del MyTestResult
        
        if NB_Adapters_Detected!=0:
            Adapters_List=[]

            #Get Ports Information
            # Default_Int_Array=[-1]* int(NB_Adapters_Detected)
            # Default_Str_Array=['']* int(NB_Adapters_Detected)

            #Retrieve Information
            Adapters_List=Get_USBEth_Adapters_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID, int(NB_Adapters_Detected))

            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('Get USB Ethernet Adapters Port','Fail',int(NB_Adapters_Detected),[],[],'This test retrieves USB Ethernet Adapters Port information. The test numeric results holds the USB Adapter Physical Port.',str(datetime.datetime.now()))

            
            i=0
            Test_Status_Port=True

            for i in range(len(Adapters_List)):
                
                My_Port=int(Adapters_List[i]['Port'])
                  
                MyTestResult.Test_Numeric_Results.append(str(My_Port))
                MyTestResult.Test_Expected_Numeric_Results.append('')
                
                Test_Status_Port=Test_Status_Port and (My_Port > 0)
                

            if Test_Status_Port==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResult)
            
            del MyTestResult        

            MyTestResult=SelfTest_CF.Test_Result()            
            MyTestResult.CustomInit('Get USB Ethernet Adapters Serial Number','Fail',int(NB_Adapters_Detected),[],[],'This test retrieves USB Ethernet Adapters Serial Number information. The test numeric results holds the USB Adapter Serial Number.',str(datetime.datetime.now()))
            
            i=0
            Test_Status_SerialNumber=True
            
            for i in range(len(Adapters_List)):
                
                My_SerialNumber=Adapters_List[i]['Serial_Number']                             
                MyTestResult.Test_Numeric_Results.append(My_SerialNumber)
                MyTestResult.Test_Expected_Numeric_Results.append('')
                Test_Status_SerialNumber=Test_Status_SerialNumber and (My_SerialNumber !='')             

            if Test_Status_SerialNumber==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResult)
            
            del MyTestResult
            
            #Retrieve MAC Address and IP Address            
            Adapters_List_With_MAC=Get_MAC_IP_Addresses(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,Adapters_List,MAP_SN_MAC_ADDRESS_File_Path, Testing) 

            MyTestResult=SelfTest_CF.Test_Result()
            MyTestResult.CustomInit('Get USB Ethernet MAC','Fail',int(NB_Adapters_Detected),[],[],'This test retrieves USB Ethernet Adapters Ethernet Adapter MAC Address information. The test numeric results holds the USB Adapter Ethernet Port MAC Address.',str(datetime.datetime.now()))
            
            Test_Status_MAC=True
            
            i=0
            for i in range(len(Adapters_List_With_MAC)):    
                My_MAC=Adapters_List_With_MAC[i]['MAC_Address']                      
                MyTestResult.Test_Numeric_Results.append(str(My_MAC))
                MyTestResult.Test_Expected_Numeric_Results.append('')
                Test_Status_MAC=Test_Status_MAC and (My_MAC !='')
                
            if Test_Status_MAC==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResult)
            
            del MyTestResult

            MyTestResult=SelfTest_CF.Test_Result()         
            MyTestResult.CustomInit('Get USB Ethernet IP Address','Fail',int(NB_Adapters_Detected),[],[],'This test retrieves USB Ethernet Adapters Ethernet Adapter IP Address information. The test numeric results holds the USB Adapter Ethernet Port IP Address.',str(datetime.datetime.now()))

            Test_Status_IP=True
            i=0
            for i in range(len(Adapters_List_With_MAC)):    
                My_IP=Adapters_List_With_MAC[i]['IP_Address']                      
                MyTestResult.Test_Numeric_Results.append(My_IP)
                MyTestResult.Test_Expected_Numeric_Results.append('')
                Test_Status_IP=Test_Status_IP and (My_IP !='')
                
            if Test_Status_IP==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResult)
            
            del MyTestResult        
                                         
            i=0
            MyTestResult=SelfTest_CF.Test_Result()         
            MyTestResult.CustomInit('Ping Interfaces','Fail',int(NB_Adapters_Detected),[],[],'This test sends ping commands to each USB->Ethernet interfaces. The test numeric results holds the error code returned by ping command (0=no error).',str(datetime.datetime.now()))
            Test_Status_Ping=True

            for i in range(len(Adapters_List_With_MAC)):    
                error=Ping_Interface(IP_Ping_Source, Adapters_List_With_MAC[i]['IP_Address'], 2)            
                if error==0: MyTestResult.Test_Numeric_Results.append('Ping successful')
                else: MyTestResult.Test_Numeric_Results.append('Ping failed')
                MyTestResult.Test_Expected_Numeric_Results.append('Ping successful')
                Test_Status_Ping=Test_Status_Ping and (error=='Ping successful')
                
            if Test_Status_Ping==True:
                MyTestResult.Test_PassFail_Status='Pass'
            else:
                MyTestResult.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResult)
          
            del MyTestResult        

 
    except:
       print(f'{"":25}\tERROR\t{"Ethernet Ports Exception.":60}')    
    
    finally:
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    return My_Module_Result 

