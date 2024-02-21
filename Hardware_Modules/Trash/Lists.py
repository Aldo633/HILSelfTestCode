import sys
import os
sys.path.append(os.path.join('C:\\','git','Tesla_BMS_HILTester','examples'))
import SelfTest_CF

JSON_TEST_FILE = "c:\\git\\Tesla_BMS_HILTester\\examples\\Trash\\Toto.json"

      
#Synthesize Test Data
SelfTest_CF.My_Tests_Result_list=[]
SelfTest_CF.My_Tests_Result_list.extend(SelfTest_CF.Initiate_List(12,"RMIO 0"))
SelfTest_CF.My_Tests_Result_list.extend(SelfTest_CF.Initiate_List(4,"RMIO 1"))
SelfTest_CF.My_Tests_Result_list.extend(SelfTest_CF.Initiate_List(7,"DAQ  0"))
SelfTest_CF.My_Tests_Result_list.extend(SelfTest_CF.Initiate_List(11,"DAQ  1"))
SelfTest_CF.My_Tests_Result_list.extend(SelfTest_CF.Initiate_List(6,"DMM  0"))

GlobalPassFail=SelfTest_CF.ComputeGlobalPassFail(SelfTest_CF.My_Tests_Result_list)

# Results Presentation
print(f"")
print(f"******************************************** GLOBAL PASS/FAIL **************************************************")
print(f"**********************************    GLOBAL Pass/Fail Result: {GlobalPassFail}    *****************************************")
print(f"****************************************************************************************************************")
print(f"")
print(f"*************************************** Tests Table (Tests Failed Only) ****************************************")
#print(f"Timestamp               \tTest Index   \tTest Module \tTest Name           \tPass/Fail?\tNB Meas.")
print(f"Timestamp               \tTest Index   \tTest Module \tTest Name")
for i in range(len(SelfTest_CF.My_Tests_Result_list)):
    if SelfTest_CF.My_Tests_Result_list[i].Test_PassFail_Status=='Fail':
        #print(f"[{str(My_Tests_Result_list[i].Test_Timestamp)}]\t{i+1}         \t{My_Tests_Result_list[i].Test_Module_Name}\t        Test {My_Tests_Result_list[i].Test_Name:4}\t        {My_Tests_Result_list[i].Test_PassFail_Status}\t        {My_Tests_Result_list[i].Test_Number_Of_Measurements}")
        print(f"[{str(SelfTest_CF.My_Tests_Result_list[i].Test_Timestamp)}]\t{i+1}         \t{SelfTest_CF.My_Tests_Result_list[i].Test_Module_Name}\t        Test {SelfTest_CF.My_Tests_Result_list[i].Test_Name:100}")
print(f"*********************************************** Test completed *************************************************")

#JSON Serialization/Deserialization
#---- Serialization
print(f"NB tests logged to file: {len(SelfTest_CF.My_Tests_Result_list)}")
SelfTest_CF.json_serialize(SelfTest_CF.My_Tests_Result_list, JSON_TEST_FILE)
#---- Deserialization
SelfTest_CF.My_TestResult_fromFile=SelfTest_CF.json_load_file(JSON_TEST_FILE)
print(f"NB tests read back from file: {len(SelfTest_CF.My_TestResult_fromFile)}")
print(f"*********************************************** Read completed *************************************************")
