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
import pythoncom

from datetime import datetime, timedelta

from pathlib import Path
from os.path import abspath
from inspect import getsourcefile
import errno
#################################################### Path/ Directories
global src_file_name
#src_file_name =  Path(__file__).stem
src_file_name=Path(abspath(getsourcefile(lambda:0))).stem
#print(__file__)
print(src_file_name)

# src_file_name=os.path.basename(__file__)
# #src_file_name=os.path.dirname(os.path.abspath("__file__")).stem
# print(src_file_name)
##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))

from path import CONFIG_PATH
from path import RESULTS_DIR_PATH
from path import LOG_DIR_PATH
############################################################## logging
global LOG_DIR_PATH
LOG_DIR_PATH=os.path.join(LOG_DIR_PATH, src_file_name.replace('\n', ''))
print(src_file_name)
print(LOG_DIR_PATH)

if not os.path.exists(LOG_DIR_PATH):
    try:
        os.makedirs(LOG_DIR_PATH)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    #os.makedirs(LOG_DIR_PATH)
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

if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity' or hardware_category=='iBridge 440-221' or hardware_category=='iBridge 2':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    exit()
if  hardware_category == 'AirUnity':
    dyna_method_names1 = '20' #17
    dyna_method_names2 = '20'
    dyna_method_names3 = '20'#40
    dyna_method_names4 = '20'#43
elif hardware_category == 'AirSpeed':
    dyna_method_names1 = '20'#17
    dyna_method_names2 = '20'#20
    dyna_method_names3 = '20'#33
    dyna_method_names4 = '20'#16
elif hardware_category == 'iBridge 2' or hardware_category == 'iBridge 440-221':
    dyna_method_names5='1'
else:
    print("Invalid hardware category")
    exit()
######################################################
global remoteconnect
def remoteconnect(SIM_machine):
    global connection
    print(SIM_machine)
    #user_name =".\"SIM_machine_password
    #print(user_name)ww

    try:
        print("Establishing connection to %s" % SIM_machine)
        pythoncom.CoInitialize()
        connection = wmi.WMI(SIM_machine, user=SIM_machine_username, password=SIM_machine_password)
        print("Connection established")
    except wmi.x_wmi:
        print("Your Username and Password of " + getfqdn(SIM_machine) + " are wrong.")

#def remote_machine_name(SIM_machine):

global ssh_connect
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
    #print(NBIF_Soap_Tool_Path_without)
    #print(NBIF_Soap_Tool_Path_without+r"\\NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t2 -m " +dyna_method_names+ " -b6 -f" +NBIF_Soap_Tool_Path_without+'\\'+Filename_for_machine_csv)
    process_id, result = connection.Win32_Process.Create(CommandLine=NBIF_Soap_Tool_Path_without+r"\\NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t2 -m " +dyna_method_names+ " -b6 -f" +NBIF_Soap_Tool_Path_without+'\\'+Filename_for_machine_csv)

#    print(CommandLine)%s (NBIF_Soap_Tool_Path,netspan_ip,filename_nbi)
    if result == 0:
       print("Process started successfully: %d" % process_id)
    else:
        print("Problem creating process: %d" % result)
    #time.sleep(600)
    # print(NBIF_Soap_Tool_Path+"NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t2 -m 43 -b6 -f " +Filename_for_machine_csv)
    # ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(NBIF_Soap_Tool_Path+"NbifStatusLoadTest.exe -n "+netspan_ip+ " -d 100  -t2 -m 43 -b6 -f" +Filename_for_machine_csv)
    # opt = ssh_stdout.read()
    # error_p=ssh_stderr.read()
#    inp=ssh_stdin.read()
 #   print(error_p)
    #print(opt)
    #time.sleep(3600)
    #sshconnection(SIM_machine,Filename_for_machine_csv)

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
        text = '\n' + "Mehtod Id :" + dyna_method_names + ',' + text + ',' + "End Time: " + now.strftime(
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
while iter < 3:

    if hardware_category == 'AirUnity':
        nbif_soap_call(SIM_machine1,Filename_for_machine1,dyna_method_names1)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine2,dyna_method_names2)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine3,dyna_method_names3)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1,Filename_for_machine4,dyna_method_names4)
        close_ssh(SIM_machine1)

        time.sleep(100)
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
        print(iter)
        iter=iter+1

    elif hardware_category == 'AirSpeed':
        nbif_soap_call(SIM_machine1, Filename_for_machine1, dyna_method_names1)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1, Filename_for_machine2, dyna_method_names2)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1, Filename_for_machine3, dyna_method_names3)
        close_ssh(SIM_machine1)
        nbif_soap_call(SIM_machine1, Filename_for_machine4, dyna_method_names4)
        close_ssh(SIM_machine1)

        time.sleep(900)
        sshconnection(SIM_machine1, Filename_for_machine1)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine2)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine3)
        close_ssh(SIM_machine1)
        sshconnection(SIM_machine1, Filename_for_machine4)
        close_ssh(SIM_machine1)
        results_read(SIM_machine1, Filename_for_machine1, dyna_method_names1)
        results_read(SIM_machine1, Filename_for_machine2, dyna_method_names2)
        results_read(SIM_machine1, Filename_for_machine3, dyna_method_names3)
        results_read(SIM_machine1, Filename_for_machine4, dyna_method_names4)
        print(iter)
        iter=iter+1
