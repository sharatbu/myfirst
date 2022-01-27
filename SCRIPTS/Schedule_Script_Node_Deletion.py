# Schedule Library imported
import schedule
import time
import threading
import os
import logging
import sys
from pathlib import Path
from Node_Deletion import *
from datetime import datetime, timedelta
import os
import signal



src_file_name =  Path(__file__).stem


##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))

from path import CONFIG_PATH
from path import RESULTS_DIR_PATH
from path import LOG_DIR_PATH
from path import  ROOT_DIR

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
#print(ROOT_DIR)
SCRIPTS_PATH=os.path.join(ROOT_DIR, 'SCRIPTS')
logging.debug(SCRIPTS_PATH)

exec('print(dir())')
def deletion():

    exec(open(SCRIPTS_PATH+ r'\Node_Deletion.py').read())
    # execfile("C:\\Users\supadhyaya\\Desktop\\Python_main\\schdedule\\Update_profile_para_config_keyvalues_error.py")
    # import Update_profile_para_config_keyvalues_error
    logging.debug("Node Deletion Called")

#schedule.every(1).minute.do(deletion)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_time_1hr= (datetime.now() + timedelta(minutes=2)).strftime('%H:%M:%S')
current_time_2hr= (datetime.now() + timedelta(minutes=4)).strftime('%H:%M:%S')
current_time_3hr= (datetime.now() + timedelta(minutes=6)).strftime('%H:%M:%S')
current_time_4hr= (datetime.now() + timedelta(minutes=8)).strftime('%H:%M:%S')
current_time_5hr= (datetime.now() + timedelta(minutes=10)).strftime('%H:%M:%S')
current_time_6hr= (datetime.now() + timedelta(minutes=12)).strftime('%H:%M:%S')
current_time_7hr= (datetime.now() + timedelta(minutes=12)).strftime('%H:%M:%S')

print(current_time)
print(current_time_1hr)
print(current_time_2hr)
print(current_time_3hr)
print(current_time_4hr)
print(current_time_5hr)
print(current_time_6hr)




schedule.every().day.at(current_time).do(deletion)
schedule.every().day.at(current_time_1hr).do(deletion)
schedule.every().day.at(current_time_2hr).do(deletion)
schedule.every().day.at(current_time_3hr).do(deletion)
schedule.every().day.at(current_time_4hr).do(deletion)
schedule.every().day.at(current_time_5hr).do(deletion)
schedule.every().day.at(current_time_6hr).do(deletion)

while True:
    # Checks whether a scheduled task
    # is pending to run or not

    #time.sleep(65)
    schedule.run_pending()
    time.sleep(1)
    #iter = iter+1
    #print("Iteration no ",iter)

