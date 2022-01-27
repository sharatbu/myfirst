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
now = datetime.datetime.now()
local_file_path = os.path.join(RESULTS_DIR_PATH,src_file_name+'.csv')
#print(local_file_path)
dateprinting = 'Node Reset:  ' + '\n' + 'Start Date and time: ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'

with open(local_file_path, "w+") as myfile2:
    myfile2.write(dateprinting)

########################################## Reading from config.txt and getting IP address user and password
myvars = {}
with open(CONFIG_PATH) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
    netspan_ip = myvars['netspan_ip'].strip()
    print(netspan_ip)
    db_server_name = myvars['db_server_name'].strip()
    database_name = myvars['database_name'].strip()
    db_password = myvars['db_password'].strip()
    db_username = myvars['db_username'].strip()
    nbif_username = myvars['nbif_username'].strip()
    nbif_password = myvars['nbif_password'].strip()
    netspan_api_version = myvars['netspan_api_version'].strip()
    hardware_category = myvars['hardware_category'].strip()
    logging.debug(hardware_category)

##########################################################IP validation
regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''


def check(netspan_ip):
    if (re.search(regex, netspan_ip)):
        #print("Valid Ip address")
        return (0)

    else:
        logging.error("Enter valid Netapan Ip address")


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
url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Inventory.asmx"
headers = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeReset'}
headers_cold={'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeReset'}
logging.debug(url)
##########################################################DB
try:
        print("connecting db")
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
        crsr = conn.cursor()
        logging.debug("Successfully connected to DB %s",db_server_name)
################# Network profile with highest usage count --SQL

        sql = """
select top 1000 BoxId  from BaseStation with (nolock) where managementmode =1 and dbid in
 ( select bsdbid from %s with (nolock) where connectionstate = 0)
""" %dyna_table_name
##########select top 1000 BoxId  from BaseStation with (nolock) where managementmode =1 and dbid in ( select bsdbid from BsAir4gLte with (nolock) where connectionstate = 0)
### select top 1000 BoxId  from BaseStation with (nolock) where managementmode =1 and dbid in ( select bsdbid from BsIbMm with (nolock) where connectionstate = 0)
##select top 1000 BoxId  from BaseStation with (nolock) where managementmode =1 and dbid in ( select bsdbid from BsIb11ac with (nolock) where connectionstate = 0)
################################### Fetch node names from db script
        print(sql)
        rows = crsr.execute(sql)
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


###########################################

def NodeReset():
    str1 = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <NodeReset xmlns="http://Airspan.Netspan.WebServices">""" % (nbif_username, nbif_password)

    # str2 = """
    #             <NodeId>%s</NodeId>"""
    str3 = """
                <NodeId>"""
    str4 = """</NodeId>"""

    str5 = """
        </NodeReset>
    </soap:Body>
</soap:Envelope>"""

    str_app = ''
    for row in rows:
        # print (row[0])

        mytag = str3 + row[0] + str4
        str_app += mytag
    myxml = str1 + str_app + str5
    try:
        logging.debug("Posting the request")
        response = requests.post(url, data=myxml, headers=headers)
        #print (response.content)
        #print(response.text)
        if response.ok:
            #print('Success!')

            tree = ET.fromstring(response.content)
        # print(response.text)
            dom = ET.fromstring(response.text)
            namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://Airspan.Netspan.WebServices',
            }
            names = dom.findall(
            './soap:Body'
            '/a:NodeResetResponse'
            '/a:NodeResetResult'
            '/a:ErrorCode',
            namespaces,
        )

            #print (names)

            for name in names:
                print(name.text)
                if(name.text=='OK'):
                    logging.debug(" Node Reprovsion  Sucessfull")
                    tree = ET.fromstring(response.content)
                    dom = ET.fromstring(response.text)
                    namespaces = {
                        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                        'a': 'http://Airspan.Netspan.WebServices',
                    }
                    NodeIds = dom.findall(
                        './soap:Body'
                        '/a:NodeResetResponse'
                        '/a:NodeResetResult'
                        '/a:Node'
                        '/a:NodeId',
                        namespaces,
                    )
                    for NodeId in NodeIds:
                        print(NodeId.text)

                    # for NodeResultCode in NodeResultCodes:
                    #     if NodeResultCode.text=='OK':
                    #         dom = ET.fromstring(response.text)
                    #         namespaces = {
                    #             'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                    #             'a': 'http://Airspan.Netspan.WebServices',
                    #         }
                    #         nodeids = dom.findall(
                    #             './soap:Body'
                    #             '/a:NodeReprovisionResponse'
                    #             '/a:NodeReprovisionResult'
                    #             '/a:Node'
                    #             '/a:NodeId',
                    #             namespaces,
                    #         )
                    #         for nodeid in nodeids:
                    #             print(nodeid.text)

                        text = NodeId.text + '\n'
                        with open(local_file_path, "a+") as myfile2:
                             myfile2.write(text)

        else:
            logging.error("Paramter Update Failed check the URL or Connection with the server")
    except requests.exceptions.RequestException as e:
        logging.error(e)
##################################################### connecting db
def main():
    NodeReset()
    #NodeResetCold()

#############################################################Updated end time in spread sheet
    now = datetime.datetime.now()
    text = '\n' + 'Sucessfully Completed the Node Reprovisioning :' + '\n' + "End Date Time: " + now.strftime(
    "%Y-%m-%d %H:%M:%S")
    with open(local_file_path, "a+") as myfile2:
        myfile2.write(text)


if __name__ == '__main__':
    main()









