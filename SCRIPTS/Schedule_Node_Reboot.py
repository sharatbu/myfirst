# Schedule Library imported
import schedule
import time
import threading
import os
import logging
import sys
from pathlib import Path
from Bulk_Node_Reboot import *



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
exec('print(dir())',{})
def reboot():

    #exec(open(SCRIPTS_PATH+ r'\Bulk_Node_Reboot.py').read())
    exec(NodeReset)
    # execfile("C:\\Users\supadhyaya\\Desktop\\Python_main\\schdedule\\Update_profile_para_config_keyvalues_error.py")
    # import Update_profile_para_config_keyvalues_error
    logging.debug("Node Deletion Called")

schedule.every(1).minute.do(reboot)



iter=0
while True:
    # Checks whether a scheduled task
    # is pending to run or not

    #time.sleep(65)
    schedule.run_pending()
    time.sleep(80)
    iter = iter+1
    print("Iteration no ",iter)


