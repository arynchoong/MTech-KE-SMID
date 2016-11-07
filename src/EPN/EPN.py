# -*- coding: utf-8 -*-
"""
@author: yuelin
Written for Python version: 3.5.2

require phantomJS in folder:- 
 - can be downloaded from: http://phantomjs.org/download.html
 - and put in path as  below
"""

import json
from lxml import objectify
from selenium import webdriver
from bs4 import BeautifulSoup

import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime
from datetime import timedelta
import time
import pandas
import re

# Authentication parameters for LTA
headers = { 'AccountKey' : 'LBdfS4+RSEi4witEa6RjjQ==',
            'UniqueUserID' : '812eb03f-f3a1-421c-96de-069c59844bbb',
            'accept' : 'application/json'}
uri = 'http://datamall2.mytransport.sg/'
path_TSB = 'ltaodataservice/TrafficSpeedBands'
path_TI = 'ltaodataservice/TrafficIncidents'
path_FTL = 'ltaodataservice/FaultyTrafficLights'
path_ETT = 'ltaodataservice/EstTravelTimes'
path_RO = 'ltaodataservice/RoadOpenings'
path_RW = 'ltaodataservice/RoadWorks'

#NEA 
key = '781CF461BB6606ADC767F3B357E848ED4A6709A0B39C63D6'
urlNowcast = 'http://api.nea.gov.sg/api/WebAPI/?dataset=2hr_nowcast&keyref=' + key
urlWarning = 'http://api.nea.gov.sg/api/WebAPI/?dataset=heavy_rain_warning&keyref=' + key

# Meteorological Service Singapore Rainfall observations
urlRainfall = 'http://www.weather.gov.sg/weather-currentobservations-rainfall'

# function to return time difference in seconds
def getTimeDifference(TimeStart, TimeEnd):
    timeDiff = TimeEnd - TimeStart
    return timeDiff.total_seconds() / 60

# initialise DataFrames' columns
colTSB = ['MaximumSpeed', 'LinkID', 'RoadName', 'SpeedBand', 'RoadCategory', 'MinimumSpeed', 'Location']

while ((datetime.now().month == 11) and (datetime.now().day < 13)):

	if getTimeDifference(timewrite_5min, timeNow) > 5 :
	    # Traffic Speed Band data - updates every 5 minutes
		request = urllib.request.Request(uri + path_TSB, headers=headers)
		try:
			response = urlopen(request).read().decode('utf-8')
		except HTTPError as e:
			print (e)
		else:
			jsonObj = json.loads(response)
		    messages = jsonObj.get("value")
			dfTSB = pandas.DataFrame(messages)

	    # ESTIMATED TRAVEL TIMES data - updates every 5 minutes
		request = urllib.request.Request(uri + path_ETT, headers=headers)
		try:
			response = urlopen(request).read().decode('utf-8')
		except HTTPError as e:
			print (e)
		else:
			jsonObj = json.loads(response)
		    messages = jsonObj.get("value")
			dfETT = pandas.DataFrame(messages)
		
	    # set time for diff 5 mins
	    timewrite_5min = datetime.now()

	if getTimeDifference(timewrite_2min, timeNow) > 2 :
	    # collect Traffic Incidents data - updates every 2 minutes
        request = urllib.request.Request(uri + path_TI, headers=headers)
		try:
			response = urlopen(request).read().decode('utf-8')
		except HTTPError as e:
			print (e)
		else:
			jsonObj = json.loads(response)
		    messages = jsonObj.get("value")
			dfTI = pandas.DataFrame(messages)
		
	    # collect Faulty Traffic Lights  data - updates every 2 minutes
        request = urllib.request.Request(uri + path_FTL, headers=headers)
		try:
			response = urlopen(request).read().decode('utf-8')
		except HTTPError as e:
			print (e)
		else:
			jsonObj = json.loads(response)
		    messages = jsonObj.get("value")
			dfFTL = pandas.DataFrame(messages)

		# set time for diff 2 mins
	    timewrite_2min = datetime.now()
    
	# wait 2 minutes
	time.sleep(120)

# on exit loop:
print('exit' + datetime.now())


