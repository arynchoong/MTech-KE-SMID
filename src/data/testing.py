# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 19:37:43 2016

@author: vleung
Python version: 3.5.2
"""

import urllib
from urllib.request import urlopen

import json 
import xml.etree.ElementTree as ET
from lxml import objectify

from datetime import datetime
import time

url = 'http://api.nea.gov.sg/api/WebAPI/?dataset=heavy_rain_warning&keyref=781CF461BB6606ADC767F3B357E848ED455313756293E581'
#r = requests.get(url)
request = urllib.request.Request(url)
response = urlopen(request).read().decode('utf-8')
print(response)
parsed = objectify.parse(urlopen(request))

root = parsed.getroot()
title = root.item.warning
print(title)