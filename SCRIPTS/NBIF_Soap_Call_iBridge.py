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
import time
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
dateprinting = 'NBI Call:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

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
    NBIF_Soap_Tool_Path= myvars['NBIF_Soap_Tool_Path'].strip()

############################################Hardware category
dyna_method_names1=''
dyna_method_names2=''
dyna_method_names3=''
dyna_method_names4=''
dyna_method_names5=''

if hardware_category=='iBridge 440-221' or hardware_category=='iBridge 2':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either iBridge 440-221 or iBridge 2")
    exit()

if hardware_category == 'iBridge 2' or hardware_category == 'iBridge 440-221':
    dyna_method_names5='1'
else:
    print("Invalid hardware category")
    exit()
######################################################

def remoteconnect(SIM_machine):
    global connection
    print(SIM_machine)
    #user_name =".\"SIM_machine_password
    #print(user_name)ww

    try:
        print("Establishing connection to %s" % SIM_machine)
        connection = wmi.WMI(SIM_machine, user=SIM_machine_username, password=SIM_machine_password)
        print("Connection established")
    except wmi.x_wmi:
        print("Your Username and Password of " + getfqdn(SIM_machine) + " are wrong.")

#def remote_machine_name(SIM_machine):


def ssh_connect(SIM_machine,Filename_for_machines):
    global Filename_for_machine_csv
    Filename_for_machine_csv = Filename_for_machines + ".csv"
    print(Filename_for_machine_csv)
    global ssh

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=SIM_machine, port=22, username=SIM_machine_username, password=SIM_machine_password)
        #sftp = ssh.open_sftp()
        logging.debug("Successfully connected to node ")

        print("del /f "+NBIF_Soap_Tool_Path+"\\"+Filename_for_machine_csv)
        #print(NBIF_Soap_Tool_Path+r"\NbifStatusLoadTest.exe -n "+netspan_ip+" -d 100  -t2 -m 43 -b6 -f" +NBIF_Soap_Tool_Path+r"\\"+ Filename_for_machine_csv)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("del /f "+NBIF_Soap_Tool_Path+"\\"+Filename_for_machine_csv)
        #opt = ssh_stdout.read()
        logging.debug(ssh_stdout.read())
        logging.debug(ssh_stderr.read())

    except paramiko.AuthenticationException:
        print("Authentication failed when connecting to %s" % SIM_machine)



def nbif_soap_call(SIM_machine,Filename_for_machines,dyna_method_names):
    remoteconnect(SIM_machine)
    ssh_connect(SIM_machine,Filename_for_machines)
    #global Filename_for_machine_csv
    #Filename_for_machine_csv =Filename_for_machines+".csv"
    print(Filename_for_machine_csv)
    #nbif_file_str='"'+filename_nbi+'"'
    #print(nbif_file_str)
    NBIF_Soap_Tool_Path_without= re.escape(NBIF_Soap_Tool_Path)
    print(NBIF_Soap_Tool_Path_without)
    print(NBIF_Soap_Tool_Path_without+r"\\NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t1 -m 1 -f" +NBIF_Soap_Tool_Path_without+'\\'+Filename_for_machine_csv)

    process_id, result = connection.Win32_Process.Create(CommandLine=NBIF_Soap_Tool_Path_without+r"\\NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t1 -m 1 -f " +NBIF_Soap_Tool_Path_without+'\\'+Filename_for_machine_csv)

#    print(CommandLine)%s (NBIF_Soap_Tool_Path,netspan_ip,filename_nbi)
    if result == 0:
       print("Process started successfully: %d" % process_id)
    else:
        print("Problem creating process: %d" % result)

def sshconnection(SIM_machine,Filename_for_machines):
    Filename_for_machine_csv = Filename_for_machines + ".csv"
    files = [Filename_for_machine_csv]
    #files = [nbif_file_str]
    print(Filename_for_machine_csv)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(hostname=SIM_machine, port=22, username=SIM_machine_username, password="qaz_1234")
    sftp = ssh.open_sftp()
    #results=ssh.exec_command('hostname')
    #print(results)

    for file in files:

        file_remote = NBIF_Soap_Tool_Path +"\\" +file
        #temp_path=temp_path+"\\"
        print(file_remote)
        file_local = temp_path + file
        print(file_local)

        print(file_remote + '>>>' + file_local)
        try:
            res=sftp.get(file_remote, file_local)
            print(res)
        except OSError:
            pass


def results_read(SIM_machine,Filename_for_machines,dyna_method_names):
    Filename_for_machine_csv = Filename_for_machines + ".csv"
    readfile=temp_path+Filename_for_machine_csv
    print(readfile)
    with open(readfile) as myfile:
        content = myfile.read()

    try:
        text = re.search(r'Total Time Taken:.*?ms', content, re.DOTALL).group()
        a = str(print(text[17:-2]))
        now = datetime.now()
        text = '\n' + "Mehtod name : Alarm Method" + ',' + text + ',' + "End Time: " + now.strftime(
            "%Y-%m-%d %H:%M")

        with open(local_file_path, "a+") as myfile2:
            myfile2.write(text)

    except:
        pass

def close_ssh(SIM_machine):
    ssh.close()
    logging.debug("Closing the connection for %s" % SIM_machine )

#def remotecopy():
    #with open(local_file_path) as myfile:
   #     content = myfile.read()

    #try:
     #   text = re.search(r'Total Time Taken:.*?ms', content, re.DOTALL).group()
     #   a = str(print(text[17:-2]))

    #except:
        #text = check


Filename_for_machine1 = "SIM_machine1"
Filename_for_machine2 = "SIM_machine2"
Filename_for_machine3 = "SIM_machine3"
Filename_for_machine4 = "SIM_machine4"

#results_read(Filename_for_machine1)
#results_read(Filename_for_machine1)



#remoteconnect(SIM_machine1)
#ssh_connect(SIM_machine1)
iter = 0
while iter < 182:
    if hardware_category == 'iBridge 2':
        nbif_soap_call(SIM_machine1,Filename_for_machine1,dyna_method_names1)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine2,dyna_method_names2)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine3,dyna_method_names3)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine4,dyna_method_names4)
        close_ssh(SIM_machine1)

        time.sleep(850)
        sshconnection(SIM_machine1,Filename_for_machine1)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine2)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine3)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine4)
        close_ssh(SIM_machine1)
        results_read(SIM_machine1,Filename_for_machine1,dyna_method_names1)
        results_read(SIM_machine1,Filename_for_machine2,dyna_method_names2)
        results_read(SIM_machine1, Filename_for_machine3,dyna_method_names3)
        results_read(SIM_machine1, Filename_for_machine4,dyna_method_names4)
        close_ssh(SIM_machine1)
        print(iter)
        iter = iter + 1

#sshconnection(SIM_machine1)

#sshconnection(SIM_machine1,Filename_for_machine1)

# now = datetime.now()
# current_time = now.strftime("%H:%M:%S")
# current_time_1hr= (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
# current_time_2hr= (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
# current_time_3hr= (datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')
# current_time_4hr= (datetime.now() + timedelta(hours=3)).strftime('%H:%M:%S')
#
# #print(current_time)
# print(current_time_1hr)
# print(current_time_2hr)
# print(current_time_3hr)
# print(current_time_4hr)
# print(current_time_5hr)
# print(current_time_7hr)
#
# #schedule.every().day.at(current_time).do(db_query, 'SIM_machine1')
# schedule.every().day.at(current_time_1hr).do(connect, SIM_machine1)
# schedule.every().day.at(current_time_2hr).do(db_query, SIM_machine2)
#
#
# if __name__ == '__main__':
#
#
#
#     while True:
#         # Checks whether a scheduled task
#         # is pending to run or not
#         # time.sleep(65)
#         schedule.run_pending()
#         time.sleep(1)
