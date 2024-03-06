import os
import sys
from enum import Enum
#from lib import random
import random
import datetime
import time
import json

DEBUG_DISPLAY=True

class Test_Result(object):
    """Object used to store the Tests Results """
    def __init__(self):
        self.Test_Name = ''
        self.Test_PassFail_Status = Enum('Pass', 'Fail')
        self.Test_Number_Of_Measurements = 0
        self.Test_Numeric_Results = []
        self.Test_Expected_Numeric_Results =  []
        self.Test_Description = ''
        self.Test_Timestamp = None
 
    def CustomInit(self,Test_Name,Test_PassFail_Status,Test_Number_Of_Measurements,Test_Numeric_Results,Test_Expected_Numeric_Results,Test_Description,Test_Timestamp):
        self.Test_Name = Test_Name
        self.Test_PassFail_Status = Test_PassFail_Status
        self.Test_Number_Of_Measurements = Test_Number_Of_Measurements
        self.Test_Numeric_Results = Test_Numeric_Results
        self.Test_Expected_Numeric_Results =  Test_Expected_Numeric_Results
        self.Test_Description = Test_Description
        self.Test_Timestamp = Test_Timestamp

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
   

class Module_Result(object):
    """Object used to store the Module Results """
    def __init__(self):
        self.Test_Module_Name = ''        
        self.Status_Code=-1
        self.NB_Tests_Completed=0
        self.Module_Tests_Result_list=[]

    def toJSON(self):
        j=0
        for j in range(len(self.Module_Tests_Result_list)):
            i=0   
            for i in range(self.Module_Tests_Result_list[j].Test_Number_Of_Measurements):
                if isinstance(self.Module_Tests_Result_list[j].Test_Numeric_Results[i],int):
                    self.Module_Tests_Result_list[j].Test_Numeric_Results[i]=hex(self.Module_Tests_Result_list[j].Test_Numeric_Results[i])        
                if isinstance(self.Module_Tests_Result_list[j].Test_Numeric_Results[i],float):
                    self.Module_Tests_Result_list[j].Test_Numeric_Results[i]=format(self.Module_Tests_Result_list[j].Test_Numeric_Results[i],'.4f')                                       
            i=0
            for i in range(self.Module_Tests_Result_list[j].Test_Number_Of_Measurements):
                if isinstance(self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i],int):
                    self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i]=hex(self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i]) 
                if isinstance(self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i],float):         
                    self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i]=format(self.Module_Tests_Result_list[j].Test_Expected_Numeric_Results[i],'.4f')               

        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)      

 
def Initiate_List(NB_Items,Test_Module_Name):
    """This function simulates some Test Results """
    My_Module_Result=Module_Result()
    My_Module_Result.Test_Module_Name=Test_Module_Name
    Tests_Result_list = []

    i=0
    random_val=0

    for i in range(NB_Items):
        #My_TestResult = Test_Result('Test '+str(random.randint(1,1000)),'Fail',random.randint(1,32),[],[],'Synthetic Test Data')
        My_TestResult = Test_Result()
        My_TestResult.CustomInit('Test '+str(random.randint(1,1000)),'Fail',random.randint(1,32),[],[],'Synthetic Test Data',str(datetime.datetime.now()))

        random_val=random.randint(0,1)
        j=0
        if random_val==1 :
            My_TestResult.Test_PassFail_Status='Pass'
            for j in range(My_TestResult.Test_Number_Of_Measurements):
                random_meas=random.uniform(-10.0,10.0)
                My_TestResult.Test_Expected_Numeric_Results.append(random_meas)
                My_TestResult.Test_Numeric_Results.append(random.uniform(random_meas-0.001*random_meas,random_meas+0.001*random_meas))
        else:
            My_TestResult.Test_PassFail_Status='Fail'
            for j in range(My_TestResult.Test_Number_Of_Measurements):
                random_meas=random.uniform(-10.0,10.0)
                My_TestResult.Test_Expected_Numeric_Results.append(random_meas)
                My_TestResult.Test_Numeric_Results.append(random.uniform(random_meas+0.2*random_meas,random_meas+0.3*random_meas))
        My_TestResult.Test_Timestamp= str(datetime.datetime.now())
        Tests_Result_list.append(My_TestResult)
        i=i+1
        time.sleep(random.uniform(0.001,0.020))
        del My_TestResult
    My_Module_Result.Module_Tests_Result_list=Tests_Result_list
    My_Module_Result.NB_Tests_Completed=len(My_Module_Result.Module_Tests_Result_list)
    My_Module_Result.Status_Code=0
    return My_Module_Result



def json_serialize(My_Modules, filename):
    """Function to serialize Results to JSON and log file using "json dumps", """

    file_name_without_extension, file_extension = os.path.splitext(filename)
    Data_FilePath_With_Date= file_name_without_extension+"_"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+file_extension    
   
    i=0
    res ="["
    #res =""
    for i in range (len(My_Modules)):
        res= res + My_Modules[i].toJSON()
        if i<(len(My_Modules)-1):
            res = res+",\n"
    res=res+"]"
    f = open(Data_FilePath_With_Date, 'w')
    f.write(res)
    f.close()
    return Data_FilePath_With_Date


def json_load_file(filename):
    """Function to read back serialized Results from log file"""
        
    f = open(filename)
    obj=Test_Result()
    obj= json.load(f)
    f.close()
    return obj

def ComputeGlobalPassFail(Modules_Results:list):
    """Function to compute the Global Pass/Fail Status of the Self-Test"""
    i=0
    j=0
    Status='PASS'
    for i in range(len(Modules_Results)):
        j=0
        if Modules_Results[i].Status_Code<0:
            Status='FAIL'
            break   
        else:
            for j in range(Modules_Results[i].Module_Tests_Result_list[j].Test_Number_Of_Measurements):
                if (Modules_Results[i].Module_Tests_Result_list[j].Test_PassFail_Status=='Fail'):
                    Status='FAIL'
                break
        i=i+1
    return Status

def Test_Numeric_Test(Expected_Value,Measurement,Tolerance):
    """Function to check Test Result taking into consideration Tolerance (%)"""
    Test_Status=True
    lower_range_factor=1-(float(Tolerance)/100)
    upper_range_factor=1+(float(Tolerance)/100)
    if Expected_Value>0.0:
        if (Measurement<(lower_range_factor*Expected_Value))or(Measurement>(upper_range_factor*Expected_Value)):
            Test_Status=False
    else:
        if (Measurement<(upper_range_factor*Expected_Value))or(Measurement>(lower_range_factor*Expected_Value)):
            Test_Status=False
    return Test_Status

def Display_Debug_Info(str_message):
    """This function displays Debug execution message."""
    if (DEBUG_DISPLAY==True):
        print(f"[{str(datetime.datetime.now()):25}]\tDEBUG\t{str(str_message):60}")
    return


def Log_Test_Report_TXT(ReportFilePath, GlobalPassFail, My_Modules_Results, Display_Report, Include_Passed, Include_Failed):
 
    """This function logs the Tests Report. 
    In addition to the Modules Results, it has 3 parameters: Display_Report, Include_Passed and Include_Failed. 
    If Display_Report is True, then logged report is also displayed on Console. If 'Include_Passed' is True, then all passed Tests result are logged. If 'Include_Failed' is True, then all failed Tests result are logged."""
    ReportBody=''
    ReportBody=ReportBody+"*********************************************************** GLOBAL PASS/FAIL *****************************************************************\n"
    ReportBody=ReportBody+"*************************************************    GLOBAL Pass/Fail Result: "+str(GlobalPassFail)+"    ********************************************************\n"
    ReportBody=ReportBody+"**********************************************************************************************************************************************\n"
    ReportBody=ReportBody+"\n"
    ReportBody=ReportBody+"********************************************************* TESTS MODULES STATUS ***************************************************************\n"
    ReportBody=ReportBody+"Module Name".ljust(45)+"\t"+"Module Status".ljust(12)+"\n"
    i=0
    for i in range(len(My_Modules_Results)):
        ReportBody=ReportBody+str(My_Modules_Results[i].Test_Module_Name).ljust(45)+"\t"+str(My_Modules_Results[i].Status_Code).ljust(12)+"\n"
        i=i+1
    ReportBody=ReportBody+"\n"
    # if(Include_Passed==True):
    #     ReportBody=ReportBody+"*************************************** Tests Table (Tests Failed Only) ****************************************\n"
    #     ReportBody=ReportBody+str("Timestamp").ljust(25)+"\t"+str("Test Index").ljust(10)+"\t"+str("Test Module").ljust(15)+"\t"+str("Test Name").ljust(60)+"\n"
    #     j=0
    #     for j in range(len(My_Modules_Results)):
    #         i=0
    #         for i in range(My_Modules_Results[j].NB_Tests_Completed):
    #             if My_Modules_Results[j].Module_Tests_Result_list[i].Test_PassFail_Status=='Fail':
    #                 ReportBody=ReportBody+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Timestamp).ljust(25)+"\t"+str(i+1).ljust(10)+"\t"+str(My_Modules_Results[j].Test_Module_Name).ljust(15)+"\t"+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Name).ljust(60)+"\n"
    #             i=i+1
    #         j=j+1
    #     ReportBody=ReportBody+"\n"
    # if(Include_Failed==True):
    #     ReportBody=ReportBody+"*************************************** Tests Table (Tests Passed Only) ***************************************\n"
    #     ReportBody=ReportBody+str("Timestamp").ljust(25)+"\t"+str("Test Index").ljust(10)+"\t"+str("Test Module").ljust(15)+"\t"+str("Test Name").ljust(60)+"\n"
    #     j=0
    #     for j in range(len(My_Modules_Results)):
    #         i=0
    #         for i in range(My_Modules_Results[j].NB_Tests_Completed):
    #             if My_Modules_Results[j].Module_Tests_Result_list[i].Test_PassFail_Status=='Pass':
    #                  ReportBody=ReportBody+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Timestamp).ljust(25)+"\t"+str(i+1).ljust(10)+"\t"+str(My_Modules_Results[j].Test_Module_Name).ljust(15)+"\t"+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Name).ljust(60)+"\n"
    #             i=i+1
    #         j=j+1
    #     ReportBody=ReportBody+"\n"
    if(Include_Passed==True):
        ReportBody=ReportBody+"****************************************************** Tests Table (Tests Failed Only) *******************************************************\n"
        ReportBody=ReportBody+str("Timestamp").ljust(28)+""+str("Test Index").ljust(13)+str("Test Module").ljust(55)+str("Test Name").ljust(60)+"\n"
        j=0
        for j in range(len(My_Modules_Results)):
            i=0
            for i in range(My_Modules_Results[j].NB_Tests_Completed):
                if My_Modules_Results[j].Module_Tests_Result_list[i].Test_PassFail_Status=='Fail':
                    ReportBody=ReportBody+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Timestamp).ljust(28)+str(i+1).ljust(13)+str(My_Modules_Results[j].Test_Module_Name).ljust(55)+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Name).ljust(60)+"\n"
                i=i+1
            j=j+1
        ReportBody=ReportBody+"\n"
    if(Include_Failed==True):
        ReportBody=ReportBody+"****************************************************** Tests Table (Tests Passed Only) *******************************************************\n"
        ReportBody=ReportBody+str("Timestamp").ljust(28)+str("Test Index").ljust(13)+str("Test Module").ljust(55)+str("Test Name").ljust(60)+"\n"
        j=0
        for j in range(len(My_Modules_Results)):
            i=0
            for i in range(My_Modules_Results[j].NB_Tests_Completed):
                if My_Modules_Results[j].Module_Tests_Result_list[i].Test_PassFail_Status=='Pass':
                     ReportBody=ReportBody+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Timestamp).ljust(28)+str(i+1).ljust(13)+str(My_Modules_Results[j].Test_Module_Name).ljust(55)+str(My_Modules_Results[j].Module_Tests_Result_list[i].Test_Name).ljust(60)+"\n"
                i=i+1
            j=j+1
        ReportBody=ReportBody+"\n"

    ReportBody=ReportBody+"********************************************************** REPORT completed ******************************************************************\n\n\n"
    
    ReportBody=ReportBody+"********************************************************  Errors Documentation  **************************************************************\n"
    ReportBody=ReportBody+"NIDAQmx: https://www.ni.com/docs/en-US/bundle/ni-daqmx-.net-framework-4.5.1-class-library-getting-started/page/netdaqmxerrorcodes.html\n"
    ReportBody=ReportBody+"NI-SLSC: https://www.ni.com/en/support/documentation/supplemental/18/using-the-slsc-web-api.html\n"
    ReportBody=ReportBody+"NI-RIO (FPGA): https://labviewwiki.org/wiki/NI-RIO_Error_Code_Family\n"
     
    if Display_Report==True:
        print(ReportBody)
    file_name, file_extension = os.path.splitext(ReportFilePath)
    ReportFilePath_With_Date=file_name+"_"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+file_extension
    f = open(ReportFilePath_With_Date, 'w')
    f.write(ReportBody)
    f.close
    return
