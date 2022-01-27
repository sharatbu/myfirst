import subprocess
import re
import os
import paramiko
paramiko.util.log_to_file('/temp/temp1.txt')
paramiko.util.load_host_keys(os.path.expanduser('/temp/temp2.txt'))
import logging
import sys
import csv
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
dateprinting = 'JMeter Script Execution:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

with open(local_file_path, "a+") as myfile2:
    myfile2.write(dateprinting)

########################################## Reading from config.txt and getting IP address user and password
myvars = {}
with open(CONFIG_PATH) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
    netspan_ip = myvars['netspan_ip'].strip()
    #print(netspan_ip)
    jmeter_bin_path = myvars['jmeter_bin_path'].strip()
    jmeter_script_path = myvars['jmeter_script_path'].strip()
    jmeter_script_name = myvars['jmeter_script_name'].strip()
    jmeter_results_path = myvars['jmeter_results_path'].strip()
    jmeter_script_log_file = myvars['jmeter_script_log_file'].strip()
    log_file_name_for_read= myvars['log_file_name_for_read'].strip()
########################### Running Jmeter script locally

jmeter_bin_path_with= re.escape(jmeter_bin_path)
#print(jmeter_bin_path_with)
jmeter_script_path_with= re.escape(jmeter_script_path)
#print(jmeter_script_path_with)
jmeter_script_log_file_with= re.escape(jmeter_script_log_file)
#print(jmeter_script_path_with)
#files=jmeter_script_log_file_with+"\\"+log_file_name_for_read
rem_file=jmeter_script_log_file+"\\"+log_file_name_for_read
files=[jmeter_script_log_file+"\\"+log_file_name_for_read]
print(files)
logging.debug("Remove the if file exist")
if os.path.exists(rem_file):
    os.remove(rem_file)
else:
    logging.debug("Can not delete the file as it doesn't exists")
print(jmeter_bin_path_with+r"\\jmeter.bat -n -t "+jmeter_script_path_with +r"\\17_00_071_8.jmx -j "+ jmeter_script_log_file_with+ r"\\log.log")
p = subprocess.Popen(jmeter_bin_path_with+r"\\jmeter.bat -n -t "+jmeter_script_path_with +r"\\17_00_071_8.jmx -j "+ jmeter_script_log_file_with+ r"\\log.log -LERROR -DTHREADS=30 -DRAMP_UP=60 -DDURATION=200",
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

logging.debug(p.communicate())
logging.debug(p.returncode)
################Time update
now = datetime.now()
dateprinting = 'JMeter Script Execution:  ' + '\n' + 'End Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'+" Requests average respone time more than 10 sec" + '\n'

with open(local_file_path, "a+") as myfile2:
    myfile2.write(dateprinting)



time.sleep(10)

for file in files:
    with open(file, 'r') as f, open(local_file_path, 'a') as g:
        reader = csv.DictReader(f)
        #for record in reader:
            #print(record)
        c1, c2, c3,*_ = reader.fieldnames
        print(reader.fieldnames)
        #timeStamp, elapsedtime, label, *_ = reader.fieldnames
        print()
        writer = csv.DictWriter(g, fieldnames=(c1, c2, c3), delimiter=',')
        writer.writeheader()

        for row in reader:
            if int(row[c2]) > 10000:
                writer.writerow({c1: row[c1], c2: row[c2], c3: row[c3]})
                print(row[c2])



