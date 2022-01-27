import wmi
import subprocess
import re
import os
import logging
import sys
import schedule
import logging
import time
import pythoncom
from datetime import datetime, timedelta

from pathlib import Path
#################################################### Path/ Directories

src_file_name =  Path(__file__).stem


##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))

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

dateprinting = ''
text = ''
now = datetime.now()
local_file_path = os.path.join(RESULTS_DIR_PATH,src_file_name+'.csv')
#print(local_file_path)
dateprinting = 'Nodes online Start Time:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

with open(local_file_path, "a+") as myfile2:
    myfile2.write(dateprinting)

########################################## Reading from config.txt and getting IP address user and password

########################################## Reading from config.txt and getting IP address user and password
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
    lydia_tool_path = myvars['lydia_tool_path'].strip()
    sim1_start_port_no = myvars['sim1_start_port_no'].strip()
    sim1_end_port_no = myvars['sim1_end_port_no'].strip()
    mibwalk_file_name=myvars['mibwalk_file_name'].strip()
    granularity_period=myvars['granularity_period'].strip()

############################################Hardware category

if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity' or hardware_category=='iBridge 440-221':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221")
    exit()

######################################################

def remoteconnect(SIM_machine):
    global connection
    print(SIM_machine)
    #user_name =".\"SIM_machine_password
    #print(user_name)ww

    try:
        print("Establishing connection to %s" % SIM_machine)
        pythoncom.CoInitialize()
        connection = wmi.WMI(SIM_machine, user=SIM_machine_username, password=SIM_machine_password)
        logging.debug("Connection established with the server %s", SIM_machine)
        print("Connection established")
    except wmi.x_wmi:
        print("Your Username and Password of " + getfqdn(SIM_machine) + " are wrong.")

#def remote_machine_name(SIM_machine):
def process_kill(SIM_machine):
    remoteconnect(SIM_machine)
    pythoncom.CoInitialize()
    process_id, result = connection.Win32_Process.Create(CommandLine="taskkill /IM  Lydia.exe /F")
    if result == 0:
       logging.debug("Process terminated successfully on the server")
       print("Process Terminated successfully")
    else:
        print("Problem in Termiating the process: %d" % result)
        logging.debug("Problem  in Termiating process: %d" % result)

def nodes_online(SIM_machine,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period):
    process_kill(SIM_machine)
    time.sleep(10)
    remoteconnect(SIM_machine)
    if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity' or hardware_category=='iBridge 440-221':
        lydia_tool_path_with= re.escape(lydia_tool_path)
        print(lydia_tool_path_with+r"\\Lydia.exe -s "+sim1_start_port_no+" -e "+sim1_end_port_no+" -m "+lydia_tool_path_with+r"\\"+mibwalk_file_name+ " -g "+granularity_period)
        pythoncom.CoInitialize()

        process_id, result = connection.Win32_Process.Create(CommandLine=lydia_tool_path_with+r"\\Lydia.exe -s "+sim1_start_port_no+" -e "+sim1_end_port_no+" -m "+lydia_tool_path_with+r"\\"+mibwalk_file_name+ " -g "+granularity_period)
        if result == 0:
            logging.debug("Process started successfully on the server :%s and process id :%d" % (SIM_machine, process_id))
            print("Process Started successfully")
        else:
            print("Problem creating process: %d" % result)
            logging.debug("Problem creating process: %d" % result)
    else:
        exit()


# process_kill(SIM_machine1)
# process_kill(SIM_machine1)
# process_kill(SIM_machine2)
# process_kill(SIM_machine3)
# process_kill(SIM_machine4)
# process_kill(SIM_machine5)
# process_kill(SIM_machine6)
nodes_online(SIM_machine1,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
nodes_online(SIM_machine2,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
nodes_online(SIM_machine3,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
nodes_online(SIM_machine4,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
nodes_online(SIM_machine5,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
nodes_online(SIM_machine6,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
#trap_send(SIM_machine2,sim1_start_port_no,sim1_end_port_no,sim1_target_for_trap,sim1_no_of_traps,sim1_delay_in_traps,sim1_trap_argument)
#trap_send(SIM_machine3)
#trap_send(SIM_machine4)
#trap_send(SIM_machine5)
#trap_send(SIM_machine6)

