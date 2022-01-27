import requests
import xml.etree.ElementTree as ET
import csv
import random
import datetime
import pyodbc
import re
import schedule
import os
import logging
import sys
from pathlib import Path


src_file_name =  Path(__file__).stem
print(src_file_name)

##os.getcwd()
##print(temp_path)
##temp_path= os.path.normpath(os.getcwd() + os.sep + os.pardir)
###os.chdir("..\")

sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir))

from path import CONFIG_PATH
from path import RESULTS_DIR_PATH
from path import LOG_DIR_PATH

LOG_DIR_PATH=os.path.join(LOG_DIR_PATH, src_file_name)
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
#print(LOG_DIR_PATH)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_DIR_PATH+'\LOG.log',
                    filemode='w+')

#os.chdir("..\")

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_DIR_PATH+'\ERROR.log',
                    filemode='w')


para1 = random.randrange(0, 64, 2)
para2 = random.randrange(0, 8, 1)
para3 = random.randrange(0, 64, 2)
para4 = random.randrange(0, 8, 1)
para5 = random.randrange(0, 64, 2)
para6 = random.randrange(0, 8, 1)


################################ print current time and date in spread sheet

dateprinting = ''
text = ''
now = datetime.datetime.now()

local_file_path = os.path.join(RESULTS_DIR_PATH,src_file_name+'.csv')

#print(str(now))
#print("Current date and time using strt time:")
#print(now.strftime("%Y-%m-%d %H:%M"))

dateprinting = 'Parameter Update Network Profile:  ' + '\n' + 'Start Date and time: ' + now.strftime(
    "%Y-%m-%d %H:%M:%S")

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
    db_server_name = myvars['db_server_name'].strip()
    database_name = myvars['database_name'].strip()
    db_password = myvars['db_password'].strip()
    db_username = myvars['db_username'].strip()
    nbif_username = myvars['nbif_username'].strip()
    nbif_password = myvars['nbif_password'].strip()
    netspan_api_version = myvars['netspan_api_version'].strip()
    hardware_category=myvars['hardware_category'].strip()
    logging.debug(hardware_category)

##########################################################IP validation
regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
               25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''


def check(netspan_ip):
    if (re.search(regex, netspan_ip)):
        # print("Valid Ip address")
        return (0)

    else:
        logging.error("Enter valid Netapan Ip address")


check(netspan_ip)
###############hardware category
if hardware_category == 'AirSpeed' or hardware_category == 'AirUnity':
    logging.info(hardware_category)
else:
    logging.error("Please enter valid hardware category either AirUnity or AirSpeed")
    exit()

##################################################### connecting db
try:
    conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s' % (
        db_server_name, database_name, db_username, db_password))
    crsr = conn.cursor()
    logging.debug("Successfully connected to DB")
    ################# Network profile with highest usage count --SQL

    sql = """
   
select Name from LteMmeProfile  with (nolock) INNER JOIN
(select distinct SoftwareCategoryId,SoftwareCategoryName from NetspanProductBranding with (nolock)
   where CASE WHEN '%s'='' THEN '1' ELSE SoftwareCategoryName END =CASE WHEN '%s'='' THEN '1' ELSE '%s' END )T
   ON LteMmeProfile.ProductCategoryId=T.SoftwareCategoryId
 where DBID in 
   (select top 2 MmeProfileDBID from BsAir4gLte  with (nolock) group by MmeProfileDBID having count(MmeProfileDBID) > 0 )
   """ % (hardware_category,hardware_category,hardware_category)
    ################################### Fetch nework profile
    rows = crsr.execute(sql)
    data = crsr.fetchone()
    profile_name = data[0]
    conn.close()

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    logging.error (ex)
##    if sqlstate == '08001':
##        print("DB connection failed please check connection string")

###################################################### URL calling

#print(netspan_ip)
url = "http://" + (netspan_ip) + "/WS/" + (netspan_api_version) + "/Lte.asmx"
logging.info(url)

profile_name=''
profile_name=data[0]

headers = {'content-type': 'application/soap+xml',
           'SOAPAction': 'http://Airspan.Netspan.WebServices/NetworkProfileUpdate'}
#print(profile_name)
def NetworkProfileUpdate(nbif_username, nbif_password, profile_name, para1, para2, para3, para4, para5, para6):
    #print(nbif_username)
    #print(url)
    root = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <Credentials xmlns="http://Airspan.Netspan.WebServices">
            <Username>%s</Username>
            <Password>%s</Password>
        </Credentials>
    </soap:Header>
    <soap:Body>
        <NetworkProfileUpdate xmlns="http://Airspan.Netspan.WebServices">
            <Name>%s</Name>
            <NetworkProfile>
                  <UlPktDataPriorityList>
                    <UlPktDataPriority>
                        <TrafficType>QCI1</TrafficType>
                        <Dscp>%s</Dscp>
                        <VlanPcp>%s</VlanPcp>
                    </UlPktDataPriority>
                    <UlPktDataPriority>
                        <TrafficType>QCI2</TrafficType>
                        <Dscp>%s</Dscp>
                        <VlanPcp>%s</VlanPcp>
                    </UlPktDataPriority>
                    <UlPktDataPriority>
                        <TrafficType>QCI3</TrafficType>
                        <Dscp>%s</Dscp>
                        <VlanPcp>%s</VlanPcp>
                    </UlPktDataPriority>
                    <UlPktDataPriority>
                        <TrafficType>QCI4</TrafficType>
                        <Dscp>28</Dscp>
                        <VlanPcp>5</VlanPcp>
                    </UlPktDataPriority>
                    <UlPktDataPriority>
                        <TrafficType>QCI5</TrafficType>
                        <Dscp>40</Dscp>
                        <VlanPcp>6</VlanPcp>
                    </UlPktDataPriority>
                    <UlPktDataPriority>
                        <TrafficType>QCI6</TrafficType>
                        <Dscp>18</Dscp>
                        <VlanPcp>6</VlanPcp>
                    </UlPktDataPriority>
                </UlPktDataPriorityList>
            </NetworkProfile>
        </NetworkProfileUpdate>
    </soap:Body>
</soap:Envelope>""" % (nbif_username, nbif_password, profile_name, para1, para2, para3, para4, para5, para6)

    try:
        response = requests.post(url, data=root, headers=headers)
        #print(response.text)
        if response.ok:
            logging.debug(" Paramter Update Sucessfull")
            tree = ET.fromstring(response.content)
            # print(response.text)
            dom = ET.fromstring(response.text)
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'a': 'http://Airspan.Netspan.WebServices',
            }
            names = dom.findall(
            './soap:Body'
            '/a:NetworkProfileUpdateResponse'
            '/a:NetworkProfileUpdateResult'
            '/a:ErrorCode',
            namespaces,
            )
        # print (names)

            for name in names:
                logging.debug(name.text)

            #################################################
            now = datetime.datetime.now()
            text = '\n' + 'Node Paramter Completed:' + name.text + '\n' + "End Date Time: " + now.strftime(
                "%Y-%m-%d %H:%M:%S")

            with open(local_file_path, "a") as myfile2:
                myfile2.write(text)


        #################################################
        else:
            logging.error("Paramter Update Failed check the URL or Connection with the server")
    except requests.exceptions.RequestException as e:
        logging.error(e)

        # print("%s,%s.%s" %(Username, Password,NodeNameOrId))

    profile_name = ''
    profile_name = data[0]
        ##print(strname)


def main():

    NetworkProfileUpdate(nbif_username, nbif_password, profile_name, para1, para2, para3, para4, para5, para6)


if __name__ == '__main__':
    main()















