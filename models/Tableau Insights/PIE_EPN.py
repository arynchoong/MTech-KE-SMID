from math import radians, cos, sin, asin, sqrt
from dateutil import parser
from datetime import datetime
import time
import csv
import os

class Expressway():
    def __init__(self,RoadName,ExitOrEntranceNumber,ExitOrEntrance,Direction,Latitude,Longtitude):
        self.RoadName = RoadName
        self.ExitOrEntranceNumber = ExitOrEntranceNumber 
        self.ExitOrEntrance = ExitOrEntrance #Entrance (0), Exit (1)
        self.Direction = Direction #0=Towards East, 1=Towards West
        self.Latitude = Latitude
        self.Longtitude = Longtitude

def ReadFromExpresswayCsv(CsvFileName, ExpresswayArray):
    with open(CsvFileName, 'r') as csvfile:
        PieReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')    
        for row in PieReader:
#           print (row['RoadName'],row['ExitOrEntranceNumber'],row['ExitOrEntrance'],row['Direction'],row['Latitude'],row['Longtitude'])
            ExpresswayArray.append(Expressway(row['RoadName'],row['ExitOrEntranceNumber'],row['ExitOrEntrance'],row['Direction'],row['Latitude'],row['Longtitude']))

def Point2PointDistance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

#Direction : 0=Towards East, 1=Towards West
def FindNearestExit(latitude,longtitude,ExpresswayArray,Direction):
    NearestDistanceSoFar = 1000
    NearestExit = []
    for row in ExpresswayArray:
        if (int(row.Direction) == int(Direction)) and (int(row.ExitOrEntrance) == 1):
            CurrentDistance = Point2PointDistance(float(row.Longtitude), float(row.Latitude), longtitude, latitude)
            if (CurrentDistance < NearestDistanceSoFar):
                if (latitude > float(row.Latitude)) and (Direction==1):
#                    print ("Nearest Exit is ", row.RoadName)
                    NearestDistanceSoFar = CurrentDistance
                    NearestExit = row
                elif (latitude < float(row.Latitude)) and (Direction==0):
#                    print ("Nearest Exit is ", row.RoadName)
                    NearestDistanceSoFar = CurrentDistance
                    NearestExit = row
    return NearestExit
PieArray = []
ReadFromExpresswayCsv("pie.csv", PieArray)

def ConvertToDate(DateTimeStampString):
    DateTimeStamp = datetime.strptime(DateTimeStampString, '%d/%m/%Y %H:%M')
    return (str(DateTimeStamp.month) + "/" + str(DateTimeStamp.day) + "/" + str(DateTimeStamp.year))
def ConvertToTime(DateTimeStampString):
    DateTimeStamp = datetime.strptime(DateTimeStampString, '%d/%m/%Y %H:%M')
    return (str(DateTimeStamp.hour) + ":" + str(DateTimeStamp.minute))
def FindNearestEntrance(latitude,longtitude,ExpresswayArray,Direction):
    NearestDistanceSoFar = 1000
    NearestEntrance = []
    for row in ExpresswayArray:
        if (int(row.Direction) == int(Direction)) and (int(row.ExitOrEntrance) == 0):
            CurrentDistance = Point2PointDistance(float(row.Longtitude), float(row.Latitude), longtitude, latitude)
            if (CurrentDistance < NearestDistanceSoFar):
                if (latitude < float(row.Latitude)) and (Direction==1):
#                    print ("Nearest Exit is ", row.RoadName)
                    NearestDistanceSoFar = CurrentDistance
                    NearestEntrance = row
                elif (latitude > float(row.Latitude)) and (Direction==0):
#                    print ("Nearest Exit is ", row.RoadName)
                    NearestDistanceSoFar = CurrentDistance
                    NearestEntrance = row
    return NearestEntrance
def FindTrafficIndentMessage(RoadName, TSBDateTime, Direction):
    if (Direction == 1):
        DirectionString = " (towards Tuas)"
    else:
        DirectionString = " (towards Changi Airport)"
    with open("TI2016-11-03 - Interim.csv", 'r') as csvfile:
        TiReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in TiReader:            
            if (('on '+ RoadName + DirectionString) in row['Message']):
                IncidentDateTimeStamp = datetime.strptime(row['Date Time'], '%d/%m/%Y %H:%M')
                if (IncidentDateTimeStamp > TSBDateTime):
                    TimeDiff = IncidentDateTimeStamp - TSBDateTime
                    #print (str(TimeDiff.seconds))
                    if (TimeDiff.seconds < 130):
                        IncidentLat = row['Latitude']
                        IncidentLong = row['Longitude']
                        return (row['Date Time'] + "," + row['Latitude'] + "," + row['Longitude'] + "," + row['Message'] + "," + row['Type'])
        IncidentLat = "Nothing"
        IncidentLong = "Nothing"
        return "No Message Found"

def EPN_Processing():
    if (os.path.isfile('Messaging.csv')):
        os.remove('Messaging.csv')
    with open('Messaging.csv','a') as file:
        file.write("Date,Time,MaximumSpeed,RoadName,SpeedBand,MinimumSpeed,Message\n")
    global CurrentDateTimeStamp
    global CurrentHourlySpeedBand
    global RunningHourlyAverageSpeedBand
    global SpeedBandActivateTriggerLimit
    global SpeedBandDeactivateTriggerLimit
    global TargetDirection
    CurrentHourlySpeedBand = 4
    RunningHourlyAverageSpeedBand = 4
    SpeedBandActivateTriggerLimit = 3.001
    SpeedBandDeactivateTriggerLimit = 3.782
#    SpeedBandActivateTriggerLimit = 3.351
#    SpeedBandDeactivateTriggerLimit = 3.850
    TriggerActivated = False
    TargetRoadName = "PAN ISLAND EXPRESSWAY"
    EnableHourlyAveraging = False
    TargetDirection = 0 #1=West Heading, 0=East Heading
    with open("TSB2016-11-03 - Interim.csv", 'r') as csvfile:
        TsbReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        RowCount = 0
        for row in TsbReader:
            if (len(row['X Start']) > 0) and (len(row['X End']) > 0) :               
                if ( float(row['X Start']) > float(row['X End']) ):
                    CurrentDirection = 0 # East Heading
                else:
                    CurrentDirection = 1 # West Heading
            else:
                CurrentDirection = 2 # unknown
            if ( (row['RoadName']==TargetRoadName) and (TargetDirection == CurrentDirection)):
                CurrentDateTimeStamp = datetime.strptime(row['Date Time'], '%d/%m/%Y %H:%M')
                CurrentHour = CurrentDateTimeStamp.hour
                CurrentHourlySpeedBand = float(row['SpeedBand'])
                if (RowCount == 0):
                    RunningHourlyAverageSpeedBand = CurrentHourlySpeedBand
                    PreviousHour = CurrentHour
                RowCount = RowCount + 1
                if (CurrentHour == PreviousHour)and(EnableHourlyAveraging==True) :
                    RunningHourlyAverageSpeedBand = (RunningHourlyAverageSpeedBand + CurrentHourlySpeedBand)/2
                else:
                    if (EnableHourlyAveraging == False):
                        RunningHourlyAverageSpeedBand = (RunningHourlyAverageSpeedBand + CurrentHourlySpeedBand)/2                        
                    #print("ChangeOfHourDetected:" + str(RunningHourlyAverageSpeedBand))
                    if (RunningHourlyAverageSpeedBand < SpeedBandActivateTriggerLimit)and(TriggerActivated==False):
                        #print (row['Date Time'],row['SpeedBand'],row['RoadName'],str(RunningHourlyAverageSpeedBand),"TRIGGER")
                        TriggerActivated = True
                        TI_Latitude = "0"
                        TI_Longtitude = "0"
                        TrafficIncidentMessage = FindTrafficIndentMessage('PIE',CurrentDateTimeStamp, TargetDirection).split(',')
                        ExitMessage = str("Nearest exit to take is " + FindNearestExit(float(TrafficIncidentMessage[1]), float(TrafficIncidentMessage[2]),PieArray,TargetDirection).RoadName)
                        EntranceMessage = str("Nearest entrance to take is " + FindNearestEntrance(float(TrafficIncidentMessage[1]), float(TrafficIncidentMessage[2]),PieArray,TargetDirection).RoadName)
                        #print (TrafficIncidentMessage)
                        CsvOutput = ConvertToDate(TrafficIncidentMessage[0]) + "," + ConvertToTime(TrafficIncidentMessage[0]) + ","
                        CsvOutput = CsvOutput + row['MaximumSpeed'] + "," + row['RoadName'] + "," + row['SpeedBand'] + "," + row['MinimumSpeed'] + ","
                        CsvOutput = CsvOutput + TrafficIncidentMessage[3] + ". " + str(ExitMessage) + ". " + str(EntranceMessage) 
                        print (CsvOutput + "," + str(RunningHourlyAverageSpeedBand))
                        with open('Messaging.csv','a') as file:
                            file.write(CsvOutput + "\n")
                        user_input = input(TrafficIncidentMessage[3] + ". " + str(ExitMessage) + ". " + str(EntranceMessage) + ". Enter to continue: ")
                    elif (TriggerActivated == True):
                        if (RunningHourlyAverageSpeedBand > SpeedBandDeactivateTriggerLimit):
                            user_input = input("Enter to continue: ")
                            #print (row['Date Time'],row['SpeedBand'],row['RoadName'],str(RunningHourlyAverageSpeedBand),"REMOVE")
                            CsvOutput = ConvertToDate(row['Date Time']) + "," + ConvertToTime(row['Date Time']) + ","
                            CsvOutput = CsvOutput + row['MaximumSpeed'] + "," + row['RoadName'] + "," + row['SpeedBand'] + "," + row['MinimumSpeed'] + "," + "Traffic back to normal!"
                            print (CsvOutput + "," + str(RunningHourlyAverageSpeedBand))
                            with open('Messaging.csv','a') as file:
                                file.write(CsvOutput + "\n")
                            TriggerActivated = False
                            user_input = input("Traffic back to normal! Enter to continue: ")
                        else:
                            CsvOutput = ConvertToDate(row['Date Time']) + "," + ConvertToTime(row['Date Time']) + ","
                            CsvOutput = CsvOutput + row['MaximumSpeed'] + "," + row['RoadName'] + "," + row['SpeedBand'] + "," + row['MinimumSpeed'] + "," + ""
                            print (CsvOutput + "," + str(RunningHourlyAverageSpeedBand))
                            with open('Messaging.csv','a') as file:
                                file.write(CsvOutput + "\n")
                    else:
                        CsvOutput = ConvertToDate(row['Date Time']) + "," + ConvertToTime(row['Date Time']) + ","
                        CsvOutput = CsvOutput + row['MaximumSpeed'] + "," + row['RoadName'] + "," + row['SpeedBand'] + "," + row['MinimumSpeed'] + "," + ""
                        print (CsvOutput + "," + str(RunningHourlyAverageSpeedBand))
                        with open('Messaging.csv','a') as file:
                            file.write(CsvOutput + "\n")
                        
                PreviousHour = CurrentHour
                  
PieArray = []
ReadFromExpresswayCsv("pie.csv", PieArray)
EPN_Processing()
