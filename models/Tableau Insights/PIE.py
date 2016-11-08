from math import radians, cos, sin, asin, sqrt
import csv

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

PieArray = []
ReadFromExpresswayCsv("pie.csv", PieArray)

# Test Samples
#1.358288, 103.700688 Nearest Exit Heading West is KJE, Heading East is Jalan Bahar
#1.349450, 103.733615 Nearest Exit Heading West is Bukit Batok Rd, Heading East is Jurong West Ave 1
print ("Nearest Exit To Avoid Jam is " + FindNearestExit(1.349450, 103.733615,PieArray,1).RoadName)
print ("Nearest Entrance To Avoid Jam " + FindNearestEntrance(1.349450, 103.733615,PieArray,1).RoadName)
