import requests
import xml.etree.ElementTree as ET
import csv
import datetime
import pyodbc
import re
import os
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import schedule
import time


src_file_name =  Path(__file__).stem


##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))

from path import CONFIG_PATH
from path import RESULTS_DIR_PATH
from path import LOG_DIR_PATH

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
dateprinting = 'Node Delete:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

with open(local_file_path, "w+") as myfile2:
    myfile2.write(dateprinting)

########################################## Reading from config.txt and getting IP address user and password
myvars = {}
with open(CONFIG_PATH) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
    netspan_ip = myvars['netspan_ip'].strip()
    #print(netspan_ip)
    db_server_name = myvars['db_server_name'].strip()
    database_name = myvars['database_name'].strip()
    db_password = myvars['db_password'].strip()
    db_username = myvars['db_username'].strip()
    nbif_username = myvars['nbif_username'].strip()
    nbif_password = myvars['nbif_password'].strip()
    netspan_api_version = myvars['netspan_api_version'].strip()
    hardware_category = myvars['hardware_category'].strip()
    Sf_Server_Ip=myvars['Sf_Server_Ip'].strip()
    Sf_Server_Username = myvars['Sf_Server_Username'].strip()
    Sf_Server_Password = myvars['Sf_Server_Password'].strip()
    Node_Delete_Server_Ip = myvars['Node_Delete_Server_Ip'].strip()
    logging.debug(hardware_category)

##########################################################IP validation
regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''


def check(Sf_Server_Ip):
    if (re.search(regex, netspan_ip)):
        #print("Valid Ip address")
        return (0)

    else:
        logging.error("Enter valid Netapan SF Ip address")


check(netspan_ip)


##################################################### hardware category and getting table name dynmicaly and executing the query

if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed which supports SF deletion")
    print("Please enter valid hardware category either AirUnity or AirSpeed")
    exit()


############################################################ node
url = "http://" + (Sf_Server_Ip) + "/ws/nodeService"
headers = {'content-type': 'application/soap+xml'}

logging.debug(url)
##########################################################DB
def db_query(SIM_machine):
    try:
        #print("connecting db")
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
        crsr = conn.cursor()
        logging.debug("Successfully connected to DB %s",db_server_name)
################# Network profile with highest usage count --SQL

        sql = """
select top 2 BoxId from BaseStation bs with (nolock) where dbid in
 ( select bsdbid from BsAir4gLte ba with (nolock) where SnmpIpAddress = '%s' ) order by bs.BoxId  desc
""" %Node_Delete_Server_Ip

################################### Fetch node names from db script
        print(sql)
        rows = crsr.execute(sql)
        for row in rows:
            main(Sf_Server_Username, Sf_Server_Password, row[0])

        if crsr.rowcount== 0:
            logging.info("Query Returned Zero rows please check environment details")
            print("Query Returned Zero rows please check environment details")
            exit()

        else:
            pass

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error (ex)


############################



#############################################
def main(Sf_Server_Username, Sf_Server_Password, hardwareId):

    root = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:inn="http://innoeye.webservice.com">
       <soapenv:Header/>
       <soapenv:Body>
          <inn:deleteNodeByHardwareId>
             <!--Optional:-->
             <username>%s</username>
             <!--Optional:-->
             <password>%s</password>
             <!--Optional:-->
             <hardwareId>%s</hardwareId>

          </inn:deleteNodeByHardwareId>
       </soapenv:Body>
    </soapenv:Envelope>""" % (Sf_Server_Username, Sf_Server_Password, hardwareId)
    try:
        logging.debug("Posting the request")
        print(url)
        response = requests.post(url, data=root, headers=headers)
        print(response.content)
        # print(response.text)
        if response.ok:
            # print('Success!')

            # print(response.content)
            # dom = ET.parse(response.text)
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'a': 'http://innoeye.webservice.com',
            }

            encoding = 'utf-8'
            test_string = str(response.content, encoding)
            test_string1 = test_string.replace('ns2:', '')
            test_string1 = test_string1.replace(':ns2', '')
            # print(test_string1)
            dom = ET.fromstring(test_string1)

            # ET.register_namespace('', 'http://innoeye.webservice.com')
            tree = ET.fromstring(test_string1)
            # print(response.content)
            names = dom.findall(
                './soap:Body''/a:deleteNodeByHardwareIdResponse''/a:nodeStatus''/a:ErrorString',
                namespaces,
            )
            # print(names)
            for name in names:
                print("Success ", name.text)
                logging.debug("Deleted the nodes")
            text = hardwareId + ',' + name.text + '\n'
            with open(local_file_path, "a+") as myfile2:
                myfile2.write(text)
        else:
            logging.error("Paramter Update Failed check the URL or Connection with the server")
    except requests.exceptions.RequestException as e:
        logging.error(e)



########################


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_time_1hr= (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
current_time_2hr= (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
current_time_3hr= (datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')
current_time_4hr= (datetime.now() + timedelta(hours=3)).strftime('%H:%M:%S')
current_time_5hr= (datetime.now() + timedelta(hours=4)).strftime('%H:%M:%S')
current_time_6hr= (datetime.now() + timedelta(hours=5)).strftime('%H:%M:%S')
current_time_7hr= (datetime.now() + timedelta(hours=6)).strftime('%H:%M:%S')

#print(current_time)
print(current_time_1hr)
print(current_time_2hr)
print(current_time_3hr)
print(current_time_4hr)
print(current_time_5hr)
print(current_time_6hr)
#schedule.every().day.at(current_time).do(db_query, 'SIM_machine1')
schedule.every().day.at(current_time_1hr).do(db_query, Node_Delete_Server_Ip)

schedule.every().day.at(current_time_2hr).do(db_query, Node_Delete_Server_Ip)
schedule.every().day.at(current_time_3hr).do(db_query, Node_Delete_Server_Ip)
schedule.every().day.at(current_time_4hr).do(db_query, Node_Delete_Server_Ip)
schedule.every().day.at(current_time_5hr).do(db_query, Node_Delete_Server_Ip)
schedule.every().day.at(current_time_6hr).do(db_query, Node_Delete_Server_Ip)


#########################
if __name__ == '__main__':

    while True:
        schedule.run_pending()
        time.sleep(1)


now = datetime.now()
text = '\n' + 'Sucessfully Completed the Node Deletion :' + '\n' + "End Date Time: " + now.strftime(
    "%Y-%m-%d %H:%M:%S")
with open(local_file_path, "a+") as myfile2:
    myfile2.write(text)









