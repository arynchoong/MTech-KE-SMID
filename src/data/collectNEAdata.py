# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 19:37:43 2016

@author: vleung
Written for Python version: 3.5.2
"""

from lxml import objectify
import urllib
from urllib.request import urlopen
from datetime import datetime
import time
import csv
import pandas
import os.path

#NEA 
key = '781CF461BB6606ADC767F3B357E848ED4A6709A0B39C63D6'
urlNowcast = 'http://api.nea.gov.sg/api/WebAPI/?dataset=2hr_nowcast&keyref=' + key
urlWarning = 'http://api.nea.gov.sg/api/WebAPI/?dataset=heavy_rain_warning&keyref=' + key

while ((datetime.now().month == 11) and (datetime.now().day < 12)):
	#setup daily params
	day = datetime.now().day
	today = datetime.now().strftime("%Y-%m-%d")
	
	#Nowcast file header
	filepath_Nowcast = '../../data/raw/Nowcast' + today + '.csv'
	if not os.path.isfile(filepath_Nowcast):
		fileNowcast = open(filepath_Nowcast, 'a', newline='')
		csvWriter = csv.writer(fileNowcast, delimiter=',')
		csvWriter.writerow(['Time', 'Forecast', 'Latitude', 'Longitude', 'Name'])
		fileNowcast.close()

	# loop every 30 mins
	while (day == datetime.now().day):
		timeNow = datetime.now()
		timestamp = datetime.now().strftime("%H:%M")
		
		# collect Nowcast data 
		with open(filepath_Nowcast, 'a', newline='') as fileNowcast: 
			request = urllib.request.Request(urlNowcast)
			parsed = objectify.parse(urlopen(request))
			root = parsed.getroot()
			timestamp = root.item.forecastIssue.get('time')
			csvWriter = csv.writer(fileNowcast, delimiter=',')
			for area in root.iter('area'):
				csvWriter.writerow([timestamp, area.get('forecast'), area.get("lat"), area.get("lon"), area.get("name")])
			           
        # wait 30 minutes
		time.sleep(1800)

	#completed a day
	print(datetime.now())

