# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 19:37:43 2016

@author: vleung
Written for Python version: 3.5.2
"""

import json
import urllib
from urllib.request import urlopen
from xml.etree import ElementTree
from datetime import datetime
from datetime import timedelta
import time
import csv

# Authentication parameters
headers = { 'AccountKey' : 'LBdfS4+RSEi4witEa6RjjQ==',
            'UniqueUserID' : '812eb03f-f3a1-421c-96de-069c59844bbb',
            'accept' : 'application/json'}

# function to return time difference in seconds
def getTimeDifference(TimeStart, TimeEnd):
    timeDiff = TimeEnd - TimeStart
    return timeDiff.total_seconds() / 60

#initialise timewrites to 10 minutes ago
tenMinsAgo = datetime.now() - timedelta(minutes=10)
timewrite_5min = timewrite_2min = tenMinsAgo
print(tenMinsAgo)
    
# Traffic Speed Bands
uri = 'http://datamall2.mytransport.sg/'
path_TSB = 'ltaodataservice/TrafficSpeedBands'
path_TI = 'ltaodataservice/TrafficIncidents'
path_FTL = 'ltaodataservice/FaultyTrafficLights'
path_ETT = 'ltaodataservice/EstTravelTimes'
path_RO = 'ltaodataservice/RoadOpenings'
path_RW = 'ltaodataservice/RoadWorks'

#RO file header
filepath_RO = '../../data/raw/RO.csv'
fileRO = open(filepath_RO, 'w', newline='')
csvWriter = csv.writer(fileRO, delimiter=',')
csvWriter.writerow(['Date', 'EventID', 'StartDate', 'EndDate', 'SvcDept', 'RoadName', 'Other'])
fileRO.close()
#RW file header
filepath_RW = '../../data/raw/RW.csv'
fileRW = open(filepath_RW, 'w', newline='')
csvWriter = csv.writer(fileRW, delimiter=',')
csvWriter.writerow(['Date', 'EventID', 'StartDate', 'EndDate', 'SvcDept', 'RoadName', 'Other'])
fileRW.close()

while (((datetime.now().month == 10) and (datetime.now().day > 24)) or ((datetime.now().month == 11) and (datetime.now().day < 5))):
    #setup daily params
    day = datetime.now().day
    today = datetime.now().strftime("%Y-%m-%d")
    #TSB file header
    filepath_TSB = '../../data/raw/TSB' + today + '.csv'
    fileTSB = open(filepath_TSB, 'w', newline='')
    csvWriter = csv.writer(fileTSB, delimiter=',')
    csvWriter.writerow(['Time', 'MaximumSpeed', 'LinkID', 'RoadName', 'SpeedBand', 'RoadCategory', 'MinimumSpeed', 'Location'])
    fileTSB.close()
    #TI file header
    filepath_TI = '../../data/raw/TI' + today + '.csv'
    fileTI = open(filepath_TI, 'w', newline='')
    csvWriter = csv.writer(fileTI, delimiter=',')
    csvWriter.writerow(['Time', 'Latitude', 'Longitude', 'Message', 'Type'])
    fileTI.close()
    #FTL file header
    filepath_FTL = '../../data/raw/FTL' + today + '.csv'
    fileFTL = open(filepath_FTL, 'w', newline='')
    csvWriter = csv.writer(fileFTL, delimiter=',')
    csvWriter.writerow(['Time', 'AlarmID', 'NodeID', 'Type', 'StartDate', 'EndDate', 'Message'])
    fileFTL.close()
    #ETT file header
    filepath_ETT = '../../data/raw/ETT' + today + '.csv'
    fileETT = open(filepath_ETT, 'w', newline='')
    csvWriter = csv.writer(fileETT, delimiter=',')
    csvWriter.writerow(['Time', 'Name', 'Direction', 'FarEndPoint', 'StartPoint', 'EndPoint', 'EstTime'])
    fileETT.close()

    # collect ROAD OPENINGS data - updates daily whenever there are updates
    with open(filepath_RO, 'a', newline='') as fileRO:              
        request = urllib.request.Request(uri + path_RO, headers=headers)
        response = urlopen(request).read().decode('utf-8')
        jsonObj = json.loads(response)
        timestamp = datetime.now().strftime("%H:%M")
        messages = jsonObj.get("value")
        csvWriter = csv.writer(fileRO, delimiter=',')
        for message in messages:
            csvWriter.writerow([today, message.get("EventID"), message.get("StartDate"), message.get("EndDate"), message.get("SvcDept"), message.get("RoadName"), message.get("Other")])

    # collect ROAD WORKS data - updates daily whenever there are updates
    with open(filepath_RW, 'a', newline='') as fileRW:              
        request = urllib.request.Request(uri + path_RW, headers=headers)
        response = urlopen(request).read().decode('utf-8')
        jsonObj = json.loads(response)
        timestamp = datetime.now().strftime("%H:%M")
        messages = jsonObj.get("value")
        csvWriter = csv.writer(fileRW, delimiter=',')
        for message in messages:
            csvWriter.writerow([today, message.get("EventID"), message.get("StartDate"), message.get("EndDate"), message.get("SvcDept"), message.get("RoadName"), message.get("Other")])

    # loop every 2 mins
    while (day == datetime.now().day):
        timeNow = datetime.now()
        
        if getTimeDifference(timewrite_5min, timeNow) > 5 :
            # collect Traffic Speed Band data - updates every 5 minutes
            with open(filepath_TSB, 'a', newline='') as fileTSB:              
                request = urllib.request.Request(uri + path_TSB, headers=headers)
                response = urlopen(request).read().decode('utf-8')
                jsonObj = json.loads(response)
                timestamp = datetime.now().strftime("%H:%M")
                messages = jsonObj.get("value")
                csvWriter = csv.writer(fileTSB, delimiter=',')
                for message in messages:
                    csvWriter.writerow([timestamp, message.get("MaximumSpeed"), message.get("LinkID"), message.get("RoadName"), message.get("SpeedBand"), message.get("RoadCategory"), message.get("MinimumSpeed"), message.get("Location")])

            # collect ESTIMATED TRAVEL TIMES data - updates every 5 minutes
            with open(filepath_ETT, 'a', newline='') as fileETT:              
                request = urllib.request.Request(uri + path_ETT, headers=headers)
                response = urlopen(request).read().decode('utf-8')
                jsonObj = json.loads(response)
                timestamp = datetime.now().strftime("%H:%M")
                messages = jsonObj.get("value")
                csvWriter = csv.writer(fileETT, delimiter=',')
                for message in messages:
                    csvWriter.writerow([timestamp, message.get("Name"), message.get("Direction"), message.get("FarEndPoint"), message.get("StartPoint"), message.get("EndPoint"), message.get("EstTime")])
            # set time for diff 5 mins
            timewrite_5min = datetime.now()

        if getTimeDifference(timewrite_2min, timeNow) > 2 :
            # collect Traffic Incidents data - updates every 2 minutes
            with open(filepath_TI, "a", newline='') as fileTI:
                request = urllib.request.Request(uri + path_TI, headers=headers)
                response = urlopen(request).read().decode('utf-8')
                jsonObj = json.loads(response)
                timestamp = datetime.now().strftime("%H:%M")
                messages = jsonObj.get("value")
                csvWriter = csv.writer(fileTI, delimiter=',')
                for message in messages:
                    csvWriter.writerow((timestamp, message.get("Latitude"), message.get("Longitude"), message.get("Message"), message.get("Type")))

            # collect Faulty Traffic Lights  data - updates every 2 minutes
            with open(filepath_FTL, "a", newline='') as fileFTL:
                request = urllib.request.Request(uri + path_FTL, headers=headers)
                response = urlopen(request).read().decode('utf-8')
                jsonObj = json.loads(response)
                timestamp = datetime.now().strftime("%H:%M")
                messages = jsonObj.get("value")
                csvWriter = csv.writer(fileFTL, delimiter=',')
                for message in messages:
                    csvWriter.writerow((timestamp, message.get("AlarmID"), message.get("NodeID"), message.get("Type"), message.get("StartDate"), message.get("EndDate"), message.get("Message")))
            # set time for diff 2 mins
            timewrite_2min = datetime.now()
            
        # wait 2 minutes
        time.sleep(120)

    #completed a day
    print(datetime.now())
    fileTSB.close()
    fileTI.close()
    fileFTL.close()
    fileETT.close()
fileRO.close()
fileRW.close()

