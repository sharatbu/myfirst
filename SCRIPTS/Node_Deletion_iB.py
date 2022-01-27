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

def check(Sf_Server_Ip):
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

    if (re.search(regex, netspan_ip)):
        #print("Valid Ip address")
        return (0)

    else:
        logging.error("Enter valid Netapan SF Ip address")


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
headers = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeDelete'}
headers1 = {'content-type': 'application/soap+xml', 'SOAPAction': 'http://Airspan.Netspan.WebServices/NodeManagementModeSet'}
logging.debug(url)
##########################################################DB
def db_query():
    global rows
    try:

        #print("connecting db")
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
        crsr = conn.cursor()
        logging.debug("Successfully connected to DB %s",db_server_name)
################# Network profile with highest usage count --SQL

        sql = """
select top 300 Name from BaseStation bs with (nolock) where dbid in
 ( select bsdbid from %s ba with (nolock) where SnmpIpAddress = '%s' ) order by bs.BoxId  desc
""" %(dyna_table_name,Node_Delete_Server_Ip)

################################### Fetch node names from db script
        print(sql)
        rows = crsr.execute(sql)
        if crsr.rowcount == 0:
            logging.info("Query Returned Zero rows please check environment details")
            print("Query Returned Zero rows please check environment details")
            exit()

        else:
            pass

        for row in rows:
            Unamange(nbif_username, nbif_password,row[0])


    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error (ex)

#############################################
def Unamange(nbif_username, nbif_password, Nodename):
    global alldata
    root = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <NodeManagementModeSet xmlns="http://Airspan.Netspan.WebServices">
            <NodeDetail>
                <NodeNameOrId>%s</NodeNameOrId>
                <ManagementMode>Unmanaged</ManagementMode>
            </NodeDetail>
        </NodeManagementModeSet>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password,Nodename)

    try:
        response = requests.post(url, data=root, headers=headers1)
        # print(response.text)
        if response.ok:
            logging.debug(" Node Unmanaged successfully")
            tree = ET.fromstring(response.content)
            # print(response.text)
            dom = ET.fromstring(response.text)
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'a': 'http://Airspan.Netspan.WebServices',
            }
            names = dom.findall(
                './soap:Body'
                '/a:NodeManagementModeSetResponse'
                '/a:NodeManagementModeSetResult'
                '/a:Node'
                '/a:Name',
                namespaces,
            )
            # print (names)

            for name in names:
                logging.debug(name.text)
                all_data=name.text
        else:
                logging.error("Node Un-Managed Failed check the URL or Connection with the server")
    except requests.exceptions.RequestException as e:
        logging.error(e)


def Deletion(rows):
    str1 = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Header>
                            <Credentials xmlns="http://Airspan.Netspan.WebServices">
                                <Username>%s</Username>
                                <Password>%s</Password>
                            </Credentials>
                        </soap:Header>
                        <soap:Body>
                            <NodeDelete xmlns="http://Airspan.Netspan.WebServices">""" % (nbif_username, nbif_password)

                    # str2 = """
                    #             <NodeId>%s</NodeId>"""
    str3 = """
                                <NodeName>"""
    str4 = """</NodeName>"""

    str5 = """
                            </NodeDelete>
                        </soap:Body>
                    </soap:Envelope>"""

    str_app = ''
    for row in rows:
        mytag = str3 + row[0] + str4
        str_app += mytag
    myxml = str1 + str_app + str5
    logging.debug("Posting the request for deletion")
    response = requests.post(url, data=myxml, headers=headers)
    if response.ok:
        print('Success!')
        tree = ET.fromstring(response.content)
                        # print(response.text)
        dom = ET.fromstring(response.text)
        namespaces = {
                            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                            'a': 'http://Airspan.Netspan.WebServices',
                        }
        nodecheck = dom.findall(
                            './soap:Body'
                            '/a:NodeDeleteResponse'
                            '/a:NodeDeleteResult'
                            '/a:ErrorCode',
                            namespaces,
                        )
                        # print (names)
        for node in nodecheck:
            print(node.text)
            if (node.text == 'OK'):
                logging.debug(" Node Deletion  Sucessfull")
                tree = ET.fromstring(response.content)
                dom = ET.fromstring(response.text)
                namespaces = {
                                    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                                    'a': 'http://Airspan.Netspan.WebServices',
                                }
                NodeIds = dom.findall(
                                    './soap:Body'
                                    '/a:NodeDeleteResponse'
                                    '/a:NodeDeleteResult'
                                    '/a:Node'
                                    '/a:Name',
                                    namespaces,
                                )
                for NodeId in NodeIds:
                    print(NodeId.text)

                    text = NodeId.text + '\n'
                    with open(local_file_path, "a+") as myfile2:
                        myfile2.write(text)

                else:
                        logging.error("Node Deletion Failed check the URL or Connection with the server")




# ##########################################
# def NodeDelete():
#     try:
#
#         # print("connecting db")
#         conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
#             db_server_name, database_name, db_username, db_password))
#         crsr = conn.cursor()
#         logging.debug("Successfully connected to DB %s", db_server_name)
#         ################# Network profile with highest usage count --SQL
#
#         sql = """
#    select top 300 Name from BaseStation bs with (nolock) where dbid in
#  ( select bsdbid from %s ba with (nolock) where SnmpIpAddress = %s and  ConnectionState = 7 ) order by bs.BoxId  desc""" % (dyna_table_name, Node_Delete_Server_Ip)
#
#         ################################### Fetch node names from db script
#         print(sql)
#         rows_del = crsr.execute(sql)
#         if crsr.rowcount == 0:
#             logging.info("Query Returned Zero rows please check environment details")
#             print("Query Returned Zero rows please check environment details")
#             exit()
#
#         else:
#             str1 = """<?xml version="1.0" encoding="utf-8"?>
#             <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
#                 <soap:Header>
#                     <Credentials xmlns="http://Airspan.Netspan.WebServices">
#                         <Username>%s</Username>
#                         <Password>%s</Password>
#                     </Credentials>
#                 </soap:Header>
#                 <soap:Body>
#                     <NodeDelete xmlns="http://Airspan.Netspan.WebServices">""" % (nbif_username, nbif_password)
#
#             # str2 = """
#             #             <NodeId>%s</NodeId>"""
#             str3 = """
#                         <NodeName>"""
#             str4 = """</NodeName>"""
#
#             str5 = """
#                     </NodeDelete>
#                 </soap:Body>
#             </soap:Envelope>"""
#
#             str_app = ''
#             for row in rows_del:
#                 mytag = str3 + row[0] + str4
#                 str_app += mytag
#             myxml = str1 + str_app + str5
#         try:
#             logging.debug("Posting the request for deletion")
#             response = requests.post(url, data=myxml, headers=headers)
#             # print (response.content)
#             # print(response.text)
#             if response.ok:
#                 print('Success!')
#                 tree = ET.fromstring(response.content)
#                 # print(response.text)
#                 dom = ET.fromstring(response.text)
#                 namespaces = {
#                     'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
#                     'a': 'http://Airspan.Netspan.WebServices',
#                 }
#                 names = dom.findall(
#                     './soap:Body'
#                     '/a:NodeDeleteResponse'
#                     '/a:NodeDeleteResult'
#                     '/a:ErrorCode',
#                     namespaces,
#                 )
#                 # print (names)
#                 for name in names:
#                     print(name.text)
#
#                     if (name.text == 'OK'):
#                         logging.debug(" Node Deletion  Sucessfull")
#                         tree = ET.fromstring(response.content)
#                         dom = ET.fromstring(response.text)
#                         namespaces = {
#                             'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
#                             'a': 'http://Airspan.Netspan.WebServices',
#                         }
#                         NodeIds = dom.findall(
#                             './soap:Body'
#                             '/a:NodeDeleteResponse'
#                             '/a:NodeDeleteResult'
#                             '/a:Node'
#                             '/a:Name',
#                             namespaces,
#                         )
#                         for NodeId in NodeIds:
#                             print(NodeId.text)
#
#                             text = NodeId.text + '\n'
#                             with open(local_file_path, "a+") as myfile2:
#                                 myfile2.write(text)
#         except pyodbc.Error as ex:
#             sqlstate = ex.args[0]
#             logging.error(ex)
#
#
#
#         else:
#             logging.error("Node Deletion Failed check the URL or Connection with the server")
#     except requests.exceptions.RequestException as e:
#         logging.error(e)




# #############################################
#
# now = datetime.now()
# current_time = now.strftime("%H:%M:%S")
#current_time_1hr= (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
# current_time_2hr= (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
# current_time_3hr= (datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')
# current_time_4hr= (datetime.now() + timedelta(hours=3)).strftime('%H:%M:%S')
# current_time_5hr= (datetime.now() + timedelta(hours=4)).strftime('%H:%M:%S')
# current_time_6hr= (datetime.now() + timedelta(hours=5)).strftime('%H:%M:%S')
# current_time_7hr= (datetime.now() + timedelta(hours=6)).strftime('%H:%M:%S')
#
# #print(current_time)
# print(current_time_1hr)
# print(current_time_2hr)
# print(current_time_3hr)
# print(current_time_4hr)
# print(current_time_5hr)
# print(current_time_6hr)
# #schedule.every().day.at(current_time).do(db_query, 'SIM_machine1')
# schedule.every().day.at(current_time_1hr).do(db_query, Node_Delete_Server_Ip)
#
# schedule.every().day.at(current_time_2hr).do(db_query, Node_Delete_Server_Ip)
# schedule.every().day.at(current_time_3hr).do(db_query, Node_Delete_Server_Ip)
# schedule.every().day.at(current_time_4hr).do(db_query, Node_Delete_Server_Ip)
# schedule.every().day.at(current_time_5hr).do(db_query, Node_Delete_Server_Ip)
# schedule.every().day.at(current_time_6hr).do(db_query, Node_Delete_Server_Ip)
#
#
# #########################
if __name__ == '__main__':
#
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

    check(netspan_ip)
    db_query()
    NodeDelete()




now = datetime.now()
text = '\n' + 'Sucessfully Completed the Node Deletion :' + '\n' + "End Date Time: " + now.strftime(
    "%Y-%m-%d %H:%M:%S")
with open(local_file_path, "a+") as myfile2:
    myfile2.write(text)









