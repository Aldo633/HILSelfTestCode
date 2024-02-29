r"""Ethernet_Ports Test Module."""

import sys
import os
import SelfTest_CF
import datetime
import time
import paramiko
import csv


Measurements=[]
average=None

class Commands:
    Count_USBEth_Adapters_Command=('./Count_USB_Devices.sh')
    Get_USBEth_Adapters_Information_Command=('./Get_USB_Devices_Information.sh')

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
        Count_Command=self.Count_USBEth_Adapters_Command+" "+str(Vendor_ID)+" "+str(Product_ID)
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
        Get_Information_Command=self.Get_USBEth_Adapters_Information_Command+" "+str(Vendor_ID)+" "+str(Product_ID)
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


    def Get_Eth_Interface_Information(self, host_ip, Machine_UserName, Machine_Password, MAC_Address):
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
        if exit_code==0:
                decoded_ssh_stdout=ssh_stdout.read().decode('utf-8')
                print(decoded_ssh_stdout)
                # # Split the output by newline
                # lines = decoded_ssh_stdout.split('\n')

                # # Extract column names from the first line
                # column_names = lines[0].split()
                # #SelfTest_CF.Display_Debug_Info('[Ethernet Ports] '+str(column_names))
                # # Initialize an empty list to store the data
                # Adapters_List = []
                # lines.pop()
                # for line in lines[1:]:
                #            # Process the remaining lines
                #             values = line.split()
                #             data_dict = {column: value for column, value in zip(column_names, values)}
                #             Adapters_List.append(data_dict)
                # SelfTest_CF.Display_Debug_Info('[Ethernet Ports] '+str(Adapters_List))
                EthName="Eth0"
                IP_Address="192.168.2.2"         
                                
        # Close SSH connection
        ssh.close()
        return EthName, IP_Address   



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

def Get_Eth_Interface_Information(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, MAC_Address):
    MyCommands = Commands()
    EthName, IP_Address=MyCommands.Get_Eth_Interface_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, MAC_Address)
    return EthName, IP_Address

def Get_MAC_IP_Addresses(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,Adapters_List,MAP_SN_MAC_ADDRESS_File_Path):
    try:
        # Read the tab-delimited file
        with open(MAP_SN_MAC_ADDRESS_File_Path, 'r') as file:
            lines = file.readlines()
            # reader=csv.reader(file,delimiter='\t')
            # next(reader) #skip the first row
            # for row in reader:
            #     (SerialNumber, MAC) = row
            #     SN_MAC_Dict[SerialNumber] = MAC            

        # Create a list of dictionaries
        SN_MAC_Dict = []

        for line in lines[1:]:
            Serial_Number, MAC_Address = line.strip().split("\t")
            SN_MAC_Dict.append({"Serial_Number": Serial_Number, "MAC_Address": MAC_Address})
                    
        #Print the resulting dictionary
        #for SN,MAC in SN_MAC_Dict.items():
        #   print(SN, MAC)
        #print(SN_MAC_Dict)
        Adapters_List_With_MAC=Adapters_List
        
        #Find MAC Addresses Match from SN_MAC
        i=0
        for i in range(len(Adapters_List)):
            target_serial_number = Adapters_List[i]['Serial_Number']
            for record in SN_MAC_Dict:
                if record["Serial_Number"] == target_serial_number:
                    print(f"MACAddress for SerialNumber {target_serial_number}: {record['MAC_Address']}")
                    #MAC found, we insert it.
                    Adapters_List_With_MAC[i]['MAC_Address']=record['MAC_Address']
                    EthName, IP_Address=Get_Eth_Interface_Information(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, Adapters_List_With_MAC[i]['MAC_Address'])
                    if EthName !='':
                        Adapters_List_With_MAC[i]['Eth_Name']=EthName
                    if IP_Address !='':
                        Adapters_List_With_MAC[i]['IP_Address']=IP_Address

    except:
        print("Exception!")
    return Adapters_List_With_MAC

def Ethernet_Ports_Operations(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,USB_Adapter_Vendor_ID, USB_Adapter_Product_ID,MAP_SN_MAC_ADDRESS_File_Path):
    
    My_Module_Result=SelfTest_CF.Module_Result()
    My_Module_Result.Test_Module_Name = "Ethernet Ports"
    My_Module_Result.Status_Code=0
    My_Module_Result.NB_Tests_Completed=0
    My_Module_Result.Module_Tests_Result_list=[]
    Tests_Result_list = []
    
    try:
        #Count Number of USB->Adapters
        NB_Adapters_Detected=0
        MyTestResult=SelfTest_CF.Test_Result()
        MyTestResult.CustomInit('Count USB Ethernet Adapters','Fail',1,[-1],[4],'This test counts number of USB Ethernet Adapters.',str(datetime.datetime.now()))
        NB_Adapters_Detected=Count_USBEth_Adapters(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID)

        MyTestResult.Test_Numeric_Results[0]=NB_Adapters_Detected

        if NB_Adapters_Detected!=MyTestResult.Test_Expected_Numeric_Results[0]:
            MyTestResult.Test_PassFail_Status='Fail'
        else:
            MyTestResult.Test_PassFail_Status='Pass'
        Tests_Result_list.append(MyTestResult)
        del MyTestResult
        
        if NB_Adapters_Detected!=0:
            Adapters_List=[]
            #Get Ports Information
            MyTestResultPort=SelfTest_CF.Test_Result()
            MyTestResultSerialNumber=SelfTest_CF.Test_Result()

            Default_Array=[-1]* int(NB_Adapters_Detected)

            MyTestResultPort.CustomInit('Get USB Ethernet Adapters Port','Fail',int(NB_Adapters_Detected),Default_Array,Default_Array,'This test retrieves USB Ethernet Adapters Port information. The test numeric results holds the USB Adapter Physical Port.',str(datetime.datetime.now()))
            MyTestResultSerialNumber.CustomInit('Get USB Ethernet Adapters Serial Number','Fail',int(NB_Adapters_Detected),Default_Array,Default_Array,'This test retrieves USB Ethernet Adapters Serial Number information. The test numeric results holds the USB Adapter Serial Number.',str(datetime.datetime.now()))
            #Retrieve Information
            Adapters_List=Get_USBEth_Adapters_Information(USB_Adapters_Machine_IP, USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword, USB_Adapter_Vendor_ID, USB_Adapter_Product_ID, int(NB_Adapters_Detected))
            
            i=0
            Test_Status_Port=True
            Test_Status_SerialNumber=True

            for i in range(len(Adapters_List)):
                
                My_Port=int(Adapters_List[i]['Port'])
                My_SerialNumber=Adapters_List[i]['Serial_Number']
                
                MyTestResultPort.Test_Numeric_Results[i]=My_Port
                Test_Status_Port=Test_Status_Port and (My_Port > 0)
                
                MyTestResultSerialNumber.Test_Numeric_Results[i]=My_SerialNumber
                Test_Status_SerialNumber=Test_Status_SerialNumber and (My_SerialNumber !='')

            if Test_Status_Port==True:
                MyTestResultPort.Test_PassFail_Status='Pass'
            else:
                MyTestResultPort.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResultPort)
            
            del MyTestResultPort         

            if Test_Status_SerialNumber==True:
                MyTestResultSerialNumber.Test_PassFail_Status='Pass'
            else:
                MyTestResultSerialNumber.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResultSerialNumber)
            
            del MyTestResultSerialNumber
            
            #Retrieve MAC Address and IP Address            
            MyTestResultMAC=SelfTest_CF.Test_Result()
            MyTestResultMAC.CustomInit('Get USB Ethernet Adapters MAC','Fail',int(NB_Adapters_Detected),Default_Array,Default_Array,'This test retrieves USB Ethernet Adapters MAC Address information. The test numeric results holds the USB Adapter Ethernet Port MAC Address.',str(datetime.datetime.now()))
            Adapters_List_With_MAC=Get_MAC_IP_Addresses(USB_Adapters_Machine_IP,USB_Adapters_Machine_UserName, USB_Adapters_Machine_UserPassword,Adapters_List,MAP_SN_MAC_ADDRESS_File_Path) 
            
            Test_Status_MAC=True
            i=0
            for i in range(len(Adapters_List)):    
                My_MAC=Adapters_List_With_MAC[i]['MAC']                      
                MyTestResultPort.Test_Numeric_Results[i]=My_MAC
                Test_Status_MAC=Test_Status_MAC and (My_MAC !='')
                
            if Test_Status_MAC==True:
                MyTestResultMAC.Test_PassFail_Status='Pass'
            else:
                MyTestResultMAC.Test_PassFail_Status='Fail'      
            Tests_Result_list.append(MyTestResultMAC)
            
            del MyTestResultMAC                       
 
    except:
       print(f'{"":25}\tERROR\t{"Ethernet Ports Exception.":60}')    
    
    finally:
        My_Module_Result.Module_Tests_Result_list=Tests_Result_list
        My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    return My_Module_Result 

