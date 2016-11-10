# -*- coding: utf-8 -*-
"""
@author: yuelin
Written for Python version: 3.5.2

require phantomJS in folder:- 
 - can be downloaded from: http://phantomjs.org/download.html
 - and put in path as  below

"""
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime
import time
import csv
import pandas
import os.path
import re

# Meteorological Service Singapore Rainfall observations
urlRainfall = 'http://www.weather.gov.sg/weather-currentobservations-rainfall'
driver = webdriver.PhantomJS(executable_path='../bin/phantomjs')
# time pattern
pattern = re.compile('[0-9]+:[0-9]+')
timewrite = datetime.now().strftime("%H:%M")

while ((datetime.now().month == 11) and (datetime.now().day < 12)):
	#setup daily params
	day = datetime.now().day
	today = datetime.now().strftime("%Y-%m-%d")
	
	# Rainfall file header
	filepath_Rainfall = '../../data/raw/Rainfall' + today + '.csv'
	if not os.path.isfile(filepath_Rainfall):
		fileRainfall = open(filepath_Rainfall, 'a', newline='')
		csvWriter = csv.writer(fileRainfall, delimiter=',')
		csvWriter.writerow(['Time', 'Station Id', '30mins', '1hour', '2hours'])
		fileRainfall.close()

	# loop every 10 mins
	while (day == datetime.now().day):
		timeNow = datetime.now()
		timestamp = datetime.now().strftime("%H:%M")
		
		# collect Rainfall data 
		with open(filepath_Rainfall, 'a', newline='') as fileRainfall: 
			try:
				driver.get(urlRainfall)
			except HTTPError as e:
				print (e)
				break
			# wait for page load
			time.sleep(2)
			html30mins = driver.page_source
			bsObj = BeautifulSoup(html30mins,"lxml")
			
			# Get data timestamp
			element = bsObj.find("img", {"id":"basemap"})
			timestamp = pattern.findall(element.attrs['src'])[0]
			# compare timestamp
			if(timewrite == timestamp):
				break
			# load 30 mins rainfall data
			dataset30mins =  bsObj.findAll("",{"class":"sgr"})
			
			# load 1 hour data 
			driver.find_element_by_id('1hour').click()
			time.sleep(1)
			html1hour = driver.page_source
			bsObj = BeautifulSoup(html1hour,"lxml")
			dataset1hour =  bsObj.findAll("",{"class":"sgr"})

			# load 2 hours data
			driver.find_element_by_id('2hours').click()
			time.sleep(1)
			html2hours = driver.page_source
			bsObj = BeautifulSoup(html2hours,"lxml")
			dataset2hours =  bsObj.findAll("",{"class":"sgr"})

			csvWriter = csv.writer(fileRainfall, delimiter=',')
			i = 0
			for data in dataset30mins:
				csvWriter.writerow([timestamp, data.get('id'), data.get_text(), dataset1hour[i].get_text(), dataset2hours[i].get_text()])
				i+=1
			
		    # wait 10 minutes
			time.sleep(300)
			timewrite = timestamp
			
	#completed a day
	print(datetime.now())

#close driver
driver.close()
