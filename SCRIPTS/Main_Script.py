import wmi
import os
import subprocess
import re
import socket, sys
import os
import paramiko
paramiko.util.log_to_file('/temp/temp1.txt')
paramiko.util.load_host_keys(os.path.expanduser('/temp/temp2.txt'))
import logging
import sys
import schedule
import logging
import threading
import pythoncom

import time
from datetime import datetime, timedelta


from pathlib import Path
#################################################### Path/ Directories

src_file_name =  Path(__file__).stem
#src_file_name=os.path.dirname(os.path.abspath("__file__"))

##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))
#
from path import CONFIG_PATH
from path import RESULTS_DIR_PATH
from path import LOG_DIR_PATH
############################################################## logging
LOG_DIR_PATH=os.path.join(LOG_DIR_PATH, src_file_name)
#print(LOG_DIR_PATH)
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_DIR_PATH+'\LOG.log',
                    filemode='w+')

logging.info(src_file_name)
################################ print current time and date spread sheet
myvars = {}
with open(CONFIG_PATH) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
    netspan_ip = myvars['netspan_ip'].strip()
    #print(netspan_ip)
    hardware_category = myvars['hardware_category'].strip()
    SIM_machine1=myvars['SIM_machine1'].strip()
    SIM_machine2 = myvars['SIM_machine2'].strip()
    SIM_machine3 = myvars['SIM_machine3'].strip()
    SIM_machine4 = myvars['SIM_machine4'].strip()
    SIM_machine5 = myvars['SIM_machine5'].strip()
    SIM_machine6 = myvars['SIM_machine6'].strip()
    SIM_machine_username= myvars['SIM_machine_username'].strip()
    SIM_machine_password= myvars['SIM_machine_password'].strip()
    temp_path = myvars['temp_path'].strip()
    NBIF_Soap_Tool_Path= myvars['NBIF_Soap_Tool_Path'].strip()
#################Calling script by test case wise
###########################Test case 1: NBIF Soap Call

logging.debug("Starting the test case 1 : NBI Call")
print("Starting the test setup")

def Nodes_Online_Lydia():
    print("Nodes online  test case called")
    import Nodes_Online_Lydia_AU_AS

def JMeter():
    print("Trapsender started ")
    import JMeter_Script_Exection_48hrs
    #exec(open('JMeter_Script_Exection_48hrs.py').read())

def Trap_Gen():
    print("Jmeter test case called")
    import Trap_Gen
    #exec(open('JMeter_Script_Exection_48hrs.py').read())

def NBIF():
    print("NBIF test case called")
    import NBIF_Soap_Call_AS_AU
    #exec(open('NBIF_Soap_Call_AS_AU.py').read())

def NodeProfile():
    print("Profile changes for  nodes test case called  5 time/day/hour")
    import Node_Profiles_Update_AU_AS
    #exec(open('Node_Profiles_Update_AU_AS.py').read())

def Profile_Parameter():
    print("Profile Prameter for  nodes test case called  1 time/day")
    import Profile_Parmeter_Update
    #exec(open('Node_Profiles_Update_AU_AS.py').read())

def Nodes_Comm_Failure():
    print("Nodes reboot : comms failure")
    import Nodes_Comm_Failure_20_AU_AS
    #exec(open('Node_Profiles_Update_AU_AS.py').read())



#JMeter()

# def sch1():
#     schedule.every().day.at("15:16").do(NBIF)
#     # print("ID of process running task 1: {}".format(os.getpid()))
#
#
# def sch2():
#     schedule.every().day.at("15:16").do(JMeter)
#     # print("ID of process running task 2: {}".format(os.getpid()))


t1 = threading.Thread(target=Nodes_Online_Lydia)
t2 = threading.Thread(target=JMeter)
t3 =threading.Thread(target=Trap_Gen)
t4 =threading.Thread(target=NBIF)
t5=threading.Thread(target=NodeProfile)
t6=threading.Thread(target=Profile_Parameter)
t7=threading.Thread(target=Nodes_Comm_Failure)
t1.start()
time.sleep(10)
t2.start()
time.sleep(10)
t3.start()
#t4.start()
time.sleep(10)
t5.start()
time.sleep(10)
t6.start()
time.sleep(10)
t7.start()




# while True:
#     # Checks whether a scheduled task
#     # is pending to run or not
#     schedule.run_pending()
#     #time.sleep(30)
