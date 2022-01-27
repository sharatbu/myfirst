import wmi
import subprocess
import re
import os
import logging
import sys
import schedule
import logging
import time
import pyodbc
import csv
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
dateprinting = 'Node offline Start Time:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

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
    server_ip_lydia_shut =myvars['server_ip_lydia_shut'].strip()
    com_off_port_no_start_ip =myvars['com_off_port_no_start_ip'].strip()
    com_start_port_no =myvars['com_start_port_no'].strip()
    com_end_port_no =myvars['com_end_port_no'].strip()
    db_server_name = myvars['db_server_name'].strip()
    database_name = myvars['database_name'].strip()
    db_password = myvars['db_password'].strip()
    db_username = myvars['db_username'].strip()
############################################Hardware category

###################################################

if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity' or hardware_category=='iBridge 440-221':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    exit()

######################################################
def initial_count():
######################## Entering initial node count
    conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (db_server_name, database_name, db_username, db_password))
    crsr = conn.cursor()
    logging.debug("Successfully connected to DB %s",db_server_name)
################# Network profile with highest usage count --SQL

    sql ="""SELECT TOP (1) DateAndTime,TotalNodes,CommLossNodes,OnlineNodes FROM NETSPANSTATS.dbo.NetworkNodeCountStatsRaw with (nolock)  order by DBID desc"""
    rows = crsr.execute(sql)
#    text= "Initial Node Count = "+ str(row[0]) + '\n'
    with open(local_file_path, "a+",newline='') as myfile2:
        writer = csv.writer(myfile2)
        writer.writerow([x[0] for x in crsr.description])  # column headers
        for row in rows:
            writer.writerow(row)


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

def nodes_reboot(SIM_machine,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period):
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
def end_count():
    iter = 0
    while iter < 4:
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
        crsr = conn.cursor()
        logging.debug("Successfully connected to DB %s", db_server_name)
        ################# Network profile with highest usage count --SQL

        sql = """SELECT TOP (2) DateAndTime,TotalNodes,CommLossNodes,OnlineNodes FROM NETSPANSTATS.dbo.NetworkNodeCountStatsRaw with (nolock)  order by DBID desc"""
        rows = crsr.execute(sql)
        #    text= "Initial Node Count = "+ str(row[0]) + '\n'
        with open(local_file_path, "a+", newline='') as myfile2:
            writer = csv.writer(myfile2)
            writer.writerow([x[0] for x in crsr.description])  # column headers
            for row in rows:
                writer.writerow(row)
        iter = iter + 1
        #print(iter)
        time.sleep(10)
    ###################################################

    dateprinting = 'Node offline End Time:  ' + '\n' + 'End time: ' + now.strftime(
        "%Y-%m-%d %H:%M:%S") + '\n'

    with open(local_file_path, "a+") as myfile2:
        myfile2.write(dateprinting)
    #############################################################


res_stop_ip = not server_ip_lydia_shut
res_reb_ib= not com_off_port_no_start_ip
logging.debug("Wait for 10 min to run")
time.sleep(600)
if res_stop_ip== True and res_reb_ib == True:
    logging.debug("Please enter valid IP to offline nodes")
    print("Please enter valid IP to offline the nodes")

elif res_stop_ip==False and res_reb_ib == False:
    logging.debug("20% node offline making nodes offline")
    initial_count()
    process_kill(server_ip_lydia_shut)
    print("inloop 2 ")
    nodes_reboot(com_off_port_no_start_ip, com_start_port_no, com_end_port_no, mibwalk_file_name, granularity_period)
    end_count()
    logging.debug("20% node Online again making nodes Online")
    initial_count()
    nodes_reboot(server_ip_lydia_shut, sim1_start_port_no,sim1_end_port_no, mibwalk_file_name, granularity_period)
    nodes_reboot(com_off_port_no_start_ip, sim1_start_port_no, sim1_end_port_no, mibwalk_file_name, granularity_period)
    end_count()
elif res_stop_ip==True and res_reb_ib == False:
    logging.debug("20% node offline making nodes offline")
    initial_count()
    print("inloop 2 ")
    nodes_reboot(com_off_port_no_start_ip, com_start_port_no, com_end_port_no, mibwalk_file_name, granularity_period)
    end_count()
    logging.debug("20% node Online again making nodes Online")
    initial_count()
    nodes_reboot(com_off_port_no_start_ip, sim1_start_port_no, sim1_end_port_no, mibwalk_file_name, granularity_period)
    end_count()
elif res_stop_ip==False and res_reb_ib == True:
    logging.debug("20% node offline making nodes offline")
    initial_count()
    process_kill(server_ip_lydia_shut)
    print("inloop 2 ")
    end_count()
    logging.debug("20% node Online again making nodes Online")
    initial_count()
    nodes_reboot(server_ip_lydia_shut, sim1_start_port_no, sim1_end_port_no, mibwalk_file_name, granularity_period)
    end_count()


# nodes_online(SIM_machine2,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
# nodes_online(SIM_machine3,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
# nodes_online(SIM_machine4,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
# nodes_online(SIM_machine5,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
# nodes_online(SIM_machine6,sim1_start_port_no,sim1_end_port_no,mibwalk_file_name,granularity_period)
#trap_send(SIM_machine2,sim1_start_port_no,sim1_end_port_no,sim1_target_for_trap,sim1_no_of_traps,sim1_delay_in_traps,sim1_trap_argument)
#trap_send(SIM_machine3)
#trap_send(SIM_machine4)
#trap_send(SIM_machine5)
#trap_send(SIM_machine6)

