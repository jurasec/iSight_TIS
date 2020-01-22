 # -*- coding: utf-8 -*-
import hashlib
import hmac
import email
import time
import json
import requests
import datetime
import sys

#### Julio C. Rodríguez Domínguez <jcrodriguez@ohkasystems.com> <jurasec@gmail.com>
#### This script download the TIS information from FireEye iSight from 7 days old
#### By the default this script will download the indicators ("fileName","domain","ip","url"), if you want a custom result, you can pass via cmd arguments the desired indicators
#### Indicator Types
#### Supported: See https://www.isightpartners.com/doc/sdk-bp-docs/#/valid_values Section "Valid values for indicators"

class APIRequestHandler(object):

    def __init__(self):
        self.URL = 'https://api.isightpartners.com'
        self.public_key = '<YOUR_PUBLIC_KEY>'
        self.private_key = '<YOUR_PRIVATE_KEY>'
        self.accept_version = '2.5'

    def run(self, argv):
        time_stamp = email.utils.formatdate(localtime=True)
        listImportFolder = "C:\\Program Files\\LogRhythm\\LogRhythm Job Manager\\config\\list_import\\"
        # starDate is 7 days before the current UTC now
        starDate = int(((datetime.datetime.utcnow() - datetime.timedelta(days=7))- datetime.datetime(1970,1,1)).total_seconds())
        endDate  = int((datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds())
        ENDPOINT = '/view/iocs?startDate='+str(starDate)+'&endDate='+str(endDate)
        accept_header = 'application/json'
        new_data = ENDPOINT + self.accept_version + accept_header + time_stamp
        #print(new_data)

        key = bytearray()
        key.extend(map(ord, self.private_key))
        hashed = hmac.new(key, new_data.encode('utf-8'), hashlib.sha256)

        headers = {
            'Accept': accept_header,
            'Accept-Version': self.accept_version,
            'X-Auth': self.public_key,
            'X-Auth-Hash': hashed.hexdigest(),
            'Date': time_stamp,
            }
        print "Request: " + self.URL + ENDPOINT

        fLog = open('downloadFireTIS.log','a+')
        fLog.write( datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S") + " - Executing request startDate= "+str(starDate)+"&endDate= "+str(endDate) + "\n")

        r = requests.get(self.URL + ENDPOINT, headers=headers, verify=False)
        status_code = r.status_code
        print('status_code = ' + str(status_code))
        json = r.json()

        if status_code == 200:
            indicators = [[]]
            idx = 1
            while idx < len(argv)-1:
                indicators.append([])
                idx+=1

            badVAlues = ("UNKNOWN","UNAVAILABLE")
            for report in json['message']:
                #print(r.text)
                idx = 0
                while idx < len(argv)-1:
                    #print "idx = " + str(idx)
                    indicator = argv[idx+1]
                    if( report[indicator] is not None and report[indicator].upper() not in badVAlues):
                        indicators[idx].append(report[indicator])
                        #print report[indicator] + "\n"
                    idx+=1
            
            idx = 0
            while idx < len(indicators):
                #print "Savinf file for indicator : " + argv[ idx + 1]
                f = open(listImportFolder + argv[idx+1] + '_iSight_TIS.txt', 'w+')
                for indicator in indicators[idx]:                    
                    f.write(indicator+"\n")
                f.close()
                idx+=1
            fLog.write( datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S") + " - Download  for " + str(argv[1:len(argv)]) + " succeeded." + "\n")
            fLog.close()
            print "Download  for " + str(argv[1:len(argv)]) + " succeeded."
        else:
            print(r.content)

if __name__ == '__main__':
    request_handler = APIRequestHandler()
    if len(sys.argv) == 1:
        request_handler.run(["fakePath","fileName","domain","ip","url"])
    else:
        request_handler.run(sys.argv)
    
