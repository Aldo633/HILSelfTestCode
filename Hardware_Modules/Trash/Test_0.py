import datetime
import time
from Lib import random
from enum import Enum

class Test_Result(object):
    """Object used to store the Tests Results """
    # def __init__(self,Test_Name,Test_PassFail_Status,Test_Number_Of_Measurements,Test_Numeric_Result,Test_Numeric_Expected_Result,Test_Description):
    #     self.Test_Name = Test_Name
    #     self.Test_PassFail_Status = Test_PassFail_Status
    #     self.Test_Number_Of_Measurements = Test_Number_Of_Measurements
    #     self.Test_Numeric_Result = Test_Numeric_Result
    #     self.Test_Numeric_Expected_Result =  Test_Numeric_Expected_Result
    #     self.Test_Description = Test_Description
    #     self.Test_Timestamp = datetime.datetime.now()

    def __init__(self):
        self.Test_Name = ''
        self.Test_PassFail_Status = Enum('Pass', 'Fail')
        self.Test_Number_Of_Measurements = 0
        self.Test_Numeric_Result = []
        self.Test_Numeric_Expected_Result =  []
        self.Test_Description = ''
        self.Test_Timestamp = datetime.datetime.now()
 
    # def CustomInit(self,Test_Name,Test_PassFail_Status,Test_Number_Of_Measurements,Test_Numeric_Result,Test_Numeric_Expected_Result,Test_Description):
    #     self.Test_Name = Test_Name
    #     self.Test_PassFail_Status = Test_PassFail_Status
    #     self.Test_Number_Of_Measurements = Test_Number_Of_Measurements
    #     self.Test_Numeric_Result = Test_Numeric_Result
    #     self.Test_Numeric_Expected_Result =  Test_Numeric_Expected_Result
    #     self.Test_Description = Test_Description
    #     self.Test_Timestamp = Test_Timestamp

    def CustomInit(self,Test_Name):
        self.Test_Name = Test_Name



My_TestResult = Test_Result()
#Test_Result.CustomInit('Test '+str(random.randint(1,1000)),'Fail',random.randint(1,32),None,None,'Synthetic Test Data',datetime.datetime.now())
#Test_Result.CustomInit('Test '+str(random.randint(1,1000)),'Fail',random.randint(1,32),[],[],'Synthetic Test Data')
My_TestResult.CustomInit('Test '+str(random.randint(1,1000)))
