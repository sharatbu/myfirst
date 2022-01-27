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
    SIM_machine1=myvars['SIM_machine1'].strip()
    SIM_machine2 = myvars['SIM_machine2'].strip()
    SIM_machine3 = myvars['SIM_machine3'].strip()
    SIM_machine4 = myvars['SIM_machine4'].strip()
    SIM_machine5 = myvars['SIM_machine5'].strip()
    SIM_machine6 = myvars['SIM_machine6'].strip()
    ConfigMode = myvars['ConfigMode'].strip()
    QosProfile_iB440 = myvars['QosProfile_iB440'].strip()
    Frequency = myvars['Frequency'].strip()
    Bandwidth = myvars['Bandwidth'].strip()
    WirelessEnabled = myvars['WirelessEnabled'].strip()
    AutoChannel = myvars['AutoChannel'].strip()
    MaximumChannelWidth = myvars['MaximumChannelWidth'].strip()
    ChannelMode = myvars['ChannelMode'].strip()
    AutoPowerMode = myvars['AutoPowerMode'].strip()
    BaseManagementProfile = myvars['BaseManagementProfile'].strip()
    AlarmProfile = myvars['AlarmProfile'].strip()
    QosProfile_iB2 = myvars['QosProfile_iB2'].strip()
    TxPower = myvars['TxPower'].strip()
    #ConfigMode = myvars['ConfigMode'].strip()


    #logging.debug(SystemDefaultProfile)

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
ib_role_name= ''

if hardware_category=='iBridge 440-221' or hardware_category=='iBridge 2':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    print("Please enter valid hardware category either AirUnity or AirSpeed or iBridge 440-221 or iBridge 2")
    exit()
if hardware_category == 'iBridge 440-221':
    dyna_table_name = 'BsIb11ac'
    ib_role_name = 'role = 1'
elif hardware_category == 'iBridge 2':
    dyna_table_name = 'BsIbMm'
    ib_role_name = 'DeviceMode =0'
else:
    print("Invalid hardware category")
    exit()
############################################################ node
url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Inventory.asmx"
headers = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeDelete'}
headers1 = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeManagementModeSet'}
logging.debug(url)
##########################################################DB
def startdb():
    global conn,crsr
    # 1. Create connection
    conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (db_server_name, database_name, db_username, db_password))
    # 2. Create a cursor object
    crsr = conn.cursor()
    logging.debug("Successfully connected to DB %s", db_server_name)

# Commit and close db
def closedb():
  # 5. Close connections
    conn.close()
def connect(SIM_machine_touse):
    startdb()
    global rows
    # 3. Create table if does not exist

    sql = """
    select top 300 Name from BaseStation bs with (nolock) where dbid in
     ( select bsdbid from %s ba with (nolock) where SnmpIpAddress = '%s' and %s) order by bs.BoxId  asc
    """ % (dyna_table_name, SIM_machine_touse,ib_role_name)
    print(sql)
    rows = crsr.execute(sql)


    if crsr.rowcount == 0:
        logging.info("Query Returned Zero rows please check environment details")
        print("Query Returned Zero rows please check environment details")
    else:
        for row in rows:
            main(nbif_username, nbif_password, row[0], ConfigMode,Frequency,Bandwidth,TxPower,QosProfile_iB440)

######################################################
def main(nbif_username, nbif_password,Nodename,ConfigMode,Frequency,Bandwidth,TxPower,QosProfile_iB440):
################################# AirUnity
    if hardware_category =='iBridge 440-221':
        url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Backhaul.asmx"
        headers = {'content-type': 'application/soap+xml',
                   'SOAPAction': 'http://Airspan.Netspan.WebServices/Ib440ConfigSet'}
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
        <Ib440ConfigSet xmlns="http://Airspan.Netspan.WebServices">
            <NodeName>%s</NodeName>
            <Ib440Details>
                <ConfigMode>%s</ConfigMode>
                <Frequency>%s</Frequency>
                <Bandwidth>%s</Bandwidth>
                <TxPower>%s</TxPower>
                <QosProfile>%s</QosProfile>
            </Ib440Details>
        </Ib440ConfigSet>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password,Nodename,ConfigMode,Frequency,Bandwidth,TxPower,QosProfile_iB440)

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
                    '/a:Ib440ConfigSetResponse'
                    '/a:Ib440ConfigSetResult'
                    '/a:ErrorCode',
                    namespaces
                )
                for name in names:
                    logging.debug(name.text)
                    text = Nodename + ',' + name.text + '\n'
                    now = datetime.now()
                    with open(local_file_path, "a+") as myfile2:
                        myfile2.write(text)
            else:
                logging.error("Profile Properties Update Failed check the URL or Connection with the server")
        except requests.exceptions.RequestException as e:
            logging.error(e)
############################################### AirStrand
    elif hardware_category =='iBridge 2':
        url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Backhaul.asmx"
        headers1 = {'content-type': 'application/soap+xml',
                   'SOAPAction': 'http://Airspan.Netspan.WebServices/IBridge2ConfigSet'}
        root = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <IBridge2ConfigSet xmlns="http://Airspan.Netspan.WebServices">
            <NodeName>%s</NodeName>
            <IBridge2Detail>
                <WirelessEnabled>%s</WirelessEnabled>
                <AutoChannel>%s</AutoChannel>
                <MaximumChannelWidth>%s</MaximumChannelWidth>
                <ChannelModes>
                    <ChannelMode>%s</ChannelMode>
                </ChannelModes>
                <AutoPowerMode>%s</AutoPowerMode>
                <BaseManagementProfile>%s</BaseManagementProfile>
                <AlarmProfile>%s</AlarmProfile>
                <QosProfile>%s</QosProfile>
            </IBridge2Detail>
        </IBridge2ConfigSet>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password, Nodename, WirelessEnabled, AutoChannel, MaximumChannelWidth,ChannelMode, AutoPowerMode,BaseManagementProfile,AlarmProfile,QosProfile_iB2)

        try:
            logging.debug("Posting the request")
            print(url)
            response = requests.post(url, data=root, headers=headers1)
            #print(response.content)
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
                ib2nodes = dom.findall(
            './soap:Body'
            '/a:IBridge2ConfigSetResponse'
            '/a:IBridge2ConfigSetResult'
            '/a:ErrorCode',
            namespaces
        )
                for ib2node in ib2nodes:
                    logging.debug(ib2node.text)

                    text = Nodename + ',' + ib2node.text + '\n'
                    now = datetime.now()
                    with open(local_file_path, "a+") as myfile2:
                        myfile2.write(text)

            else:
                logging.error("Profile Properties Update Failed check the URL or Connection with the server")
        except requests.exceptions.RequestException as e:
            logging.error(e)

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

# IP address for IB2
#schedule.every().day.at(current_time).do(db_query, 'SIM_machine1')
schedule.every().day.at(current_time_1hr).do(connect, SIM_machine1)
schedule.every().day.at(current_time_2hr).do(db_query, SIM_machine2)
# schedule.every().day.at(current_time_3hr).do(db_query, SIM_machine3)

#IP address for IB440
schedule.every().day.at(current_time_4hr).do(db_query, SIM_machine4)
schedule.every().day.at(current_time_5hr).do(db_query, SIM_machine5)
schedule.every().day.at(current_time_6hr).do(db_query, SIM_machine6)
# schedule.every().day.at(current_time_7hr).do(do_exit)



if __name__ == '__main__':



    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        # time.sleep(65)
        schedule.run_pending()
        time.sleep(1)


