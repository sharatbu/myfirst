import requests
import xml.etree.ElementTree as ET
import csv
import datetime
import pyodbc
import re
import os
import logging
import sys
import schedule
import logging
import datetime
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
dateprinting = 'Node Profile Update:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

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
    SystemDefaultProfile=myvars['SystemDefaultProfile'].strip()
    AdvancedConfigProfile = myvars['AdvancedConfigProfile'].strip()
    SecurityProfile=myvars['SecurityProfile'].strip()
    CellAdvancedConfigurationProfile = myvars['CellAdvancedConfigurationProfile'].strip()
    RadioProfile=myvars['RadioProfile'].strip()
    SIM_machine1=myvars['SIM_machine1'].strip()
    SIM_machine2 = myvars['SIM_machine2'].strip()
    SIM_machine3 = myvars['SIM_machine3'].strip()
    SIM_machine4 = myvars['SIM_machine4'].strip()
    SIM_machine5 = myvars['SIM_machine5'].strip()
    SIM_machine6 = myvars['SIM_machine6'].strip()


    logging.debug(SystemDefaultProfile)

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

dyna_table_name=''

if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity' or hardware_category=='iBridge 440-221' or hardware_category=='iBridge 2':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    exit()
if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity':
    dyna_table_name = 'BsAir4gLte'
elif hardware_category == 'iBridge 440-221':
     dyna_table_name='BsIb11ac'
elif hardware_category == 'iBridge 2':
    dyna_table_name = 'BsIbMm'
else:
    print("Invalid hardware category")
    exit()



############################################################ node
# url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Lte.asmx"
# headers = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/RelayEnbConfigSet'}
# logging.debug(url)
##########################################################DB

#Sim_machines=[SIM_machine1,SIM_machine2,SIM_machine3,SIM_machine4,SIM_machine5,SIM_machine6]

def db_query(SIM_machine):
    print("test")
    print(SIM_machine)
    try:
        #print("connecting db")
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
        crsr = conn.cursor()
        logging.debug("Successfully connected to DB %s",db_server_name)
################# Network profile with highest usage count --SQL

        sql = """
select top 2 Name from BaseStation bs with (nolock) where dbid in
 ( select bsdbid from BsAir4gLte ba with (nolock) where SnmpIpAddress = '%s' ) order by bs.BoxId  asc
""" %SIM_machine

################################### Fetch node names from db script
        print(sql)
        rows = crsr.execute(sql)
        print(type(rows))

        for row in rows:
            main(nbif_username, nbif_password, row[0], SystemDefaultProfile, AdvancedConfigProfile, SecurityProfile,
                 CellAdvancedConfigurationProfile, RadioProfile)

        #print(rows)
        #rows_count = cursor.execute(sql)
        if crsr.rowcount== 0:
            logging.info("Query Returned Zero rows please check environment details")
            print("Query Returned Zero rows please check environment details")
            exit()

        else:
            pass

    except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                logging.error (ex)



def main(nbif_username, nbif_password,boxid,SystemDefaultProfile,AdvancedConfigProfile,SecurityProfile,CellAdvancedConfigurationProfile,RadioProfile):
################################# AirUnity
    if hardware_category =='AirUnity':
        url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Lte.asmx"
        headers = {'content-type': 'application/soap+xml',
                   'SOAPAction': 'http://Airspan.Netspan.WebServices/RelayEnbConfigSet'}
        logging.debug(url)

        root = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <RelayEnbConfigSet xmlns="http://Airspan.Netspan.WebServices">
            <NodeName>%s</NodeName>
            <NodeDetail></NodeDetail>
            <EnbDetail>
                <ENodeBType>Home</ENodeBType>
                <SystemDefaultProfile>%s</SystemDefaultProfile>
                <AdvancedConfigProfile>%s</AdvancedConfigProfile>
                <SecurityProfile>%s</SecurityProfile>
                <LteCell>
                    <CellNumber>1</CellNumber>
                    <CellAdvancedConfigurationProfile>%s</CellAdvancedConfigurationProfile>
                    <RadioProfile>%s</RadioProfile>
                </LteCell>
            </EnbDetail>
        </RelayEnbConfigSet>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password,boxid,SystemDefaultProfile,AdvancedConfigProfile,SecurityProfile,CellAdvancedConfigurationProfile,RadioProfile)
        try:
            logging.debug("Posting the request")
            print(url)
            response = requests.post(url, data=root, headers=headers)
            print(response.content)
        # print(response.text)
            if response.ok:
                print('Success!')
                tree = ET.fromstring(response.content)
                # print(response.text)
                dom = ET.fromstring(response.text)
                namespaces = {
                    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'a': 'http://Airspan.Netspan.WebServices',
                }
                names = dom.findall(
                    './soap:Body'
                    '/a:RelayEnbConfigSetResponse'
                    '/a:RelayEnbConfigSetResult'
                    '/a:ErrorCode',
                    namespaces
                )
                for name in names:
                    logging.debug(name.text)
                    text = boxid + ',' + name.text + '\n'
                    now = datetime.now()
                    with open(local_file_path, "a+") as myfile2:
                        myfile2.write(text)




            else:
                logging.error("Paramter Update Failed check the URL or Connection with the server")
        except requests.exceptions.RequestException as e:
            logging.error(e)
############################################### AirStrand
    elif hardware_category =='AirSpeed':
        url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Lte.asmx"
        headers = {'content-type': 'application/soap+xml',
                   'SOAPAction': 'http://Airspan.Netspan.WebServices/EnbConfigSet'}
        root = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <EnbConfigSet xmlns="http://Airspan.Netspan.WebServices">
            <NodeName>%s</NodeName>
            <EnbDetails>
                <ENodeBType>Home</ENodeBType>
                <SystemDefaultProfile>%s</SystemDefaultProfile>
                <AdvancedConfigProfile>%s</AdvancedConfigProfile>
                <SecurityProfile>%s</SecurityProfile>
                <LteCell>
                    <CellNumber>1</CellNumber>
                    <CellAdvancedConfigurationProfile>%s</CellAdvancedConfigurationProfile>
                    <RadioProfile>%s</RadioProfile>
                </LteCell>
            </EnbDetails>
        </EnbConfigSet>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password, boxid, SystemDefaultProfile, AdvancedConfigProfile, SecurityProfile,
    CellAdvancedConfigurationProfile, RadioProfile)


        try:
            logging.debug("Posting the request")
            print(url)
            response = requests.post(url, data=root, headers=headers)
            print(response.content)
            # print(response.text)
            if response.ok:
                print('Success!')
                tree = ET.fromstring(response.content)
        # print(response.text)
                dom = ET.fromstring(response.text)
                namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://Airspan.Netspan.WebServices',
        }
                names = dom.findall(
            './soap:Body'
            '/a:EnbConfigSetResponse'
            '/a:EnbConfigSetResult'
            '/a:ErrorCode',
            namespaces
        )
                for name in names:
                    logging.debug(name.text)
                    text = boxid + ',' + name.text + '\n'
                    now = datetime.now()
                    with open(local_file_path, "a+") as myfile2:
                        myfile2.write(text)




            else:
                logging.error("Paramter Update Failed check the URL or Connection with the server")
        except requests.exceptions.RequestException as e:
            logging.error(e)

#############################################################Updated end time in spread sheet

def do_exit():
    print(local_file_path)
    now = datetime.now()
    text = '\n' + 'Sucessfully Completed the Profile Update for 1:' + '\n' + "End Date Time: " + now.strftime(
        "%Y-%m-%d %H:%M:%S")
    with open(local_file_path, "a+") as myfile2:
        myfile2.write(text)
    # db_query(Sim_machines)
    exit()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_time_1hr= (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
current_time_2hr= (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
current_time_3hr= (datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')
current_time_4hr= (datetime.now() + timedelta(hours=3)).strftime('%H:%M:%S')
current_time_5hr= (datetime.now() + timedelta(hours=4)).strftime('%H:%M:%S')
#current_time_6hr= (datetime.now() + timedelta(hours=5)).strftime('%H:%M:%S')
current_time_7hr= (datetime.now() + timedelta(hours=4,minutes=10)).strftime('%H:%M:%S')
#current_time_7hr= (datetime.now() + timedelta(hours=6)).strftime('%H:%M:%S')

#print(current_time)
print(current_time_1hr)
print(current_time_2hr)
print(current_time_3hr)
print(current_time_4hr)
print(current_time_5hr)
print(current_time_7hr)

#schedule.every().day.at(current_time).do(db_query, 'SIM_machine1')
schedule.every().day.at(current_time_1hr).do(db_query, SIM_machine1)
schedule.every().day.at(current_time_2hr).do(db_query, SIM_machine2)
schedule.every().day.at(current_time_3hr).do(db_query, SIM_machine3)
schedule.every().day.at(current_time_4hr).do(db_query, SIM_machine4)
schedule.every().day.at(current_time_5hr).do(db_query, SIM_machine5)
#schedule.every().day.at(current_time_6hr).do(db_query, SIM_machine6)
schedule.every().day.at(current_time_7hr).do(do_exit)



if __name__ == '__main__':



    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        # time.sleep(65)
        schedule.run_pending()
        time.sleep(1)











