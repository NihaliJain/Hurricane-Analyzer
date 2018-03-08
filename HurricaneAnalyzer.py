
import calendar
# import time

from pygeodesy import ellipsoidalVincenty as ev

fileName = "hurdat2-1851-2016-041117.csv"

recordProcessing = 0
recordP_sum = []  # store all of the record_processing for using outside the open_file
count = 0  # store the amount of storms
maximumSustainedWindSpeed = -1
maximumSustainedWindDate = ''
maximumSustainedWindTime = ''
landFalls = 0
dateRange = []
stormName = ''
stormYear = ''
isHurricane = False

stormInfo = {}
hurricaneInfo = {}

# all of the storms
Lat_sum = []
Lont_sum = []
time_sum = []
Lat_sums = []
Lont_sums = []
time_sums = []

# store the first Landfall index
Landfal_sum=[]
Landfal_sums=[]

# store the storm_name
stormNamesum = []


def prettify(d):
    return d[:4] + '-' + calendar.month_name[int(d[4:6])] + '-' + d[6:]


with open(fileName) as f:
    i=0
    for line in f:
        if recordProcessing == 0:  # header
            processedInfo = line.split(',')
            stormName = processedInfo[0].strip()
            stormYear = int(processedInfo[0][-4:])
            recordProcessing = int(processedInfo[2])  # store the recordProcessing number (the amount of record)here
            count += 1  # store how many storms here
            recordP_sum.append(recordProcessing)
            Lat_sum = []
            Lont_sum = []
            time_sum = []
            Landfal_sum=[]
        else:
            recordProcessing -= 1
            processedInfo = line.split(',')
            dateRange.append(processedInfo[0])
            Lat_sum.append(processedInfo[4])
            Lont_sum.append(processedInfo[5])
            time_sum.append(processedInfo[0] + " " + processedInfo[1])
            # append the next line latitude and longitude
            if maximumSustainedWindSpeed < int(processedInfo[6]):
                maximumSustainedWindSpeed = int(processedInfo[6].strip())
                maximumSustainedWindDate = processedInfo[0].strip()
                maximumSustainedWindTime = processedInfo[1].strip()
            # store the index of Landfall
            if processedInfo[2].strip() == 'L' and i!=-1:
                landFalls += 1
                Landfal_sum.append(i)
            if i !=-1:
                i+=1

            if processedInfo[3].strip() == 'HU':
                isHurricane = True

            # next storm here
            if recordProcessing == 0:
                Lat_sums.append(Lat_sum)
                Lont_sums.append(Lont_sum)
                time_sums.append(time_sum)
                Landfal_sums.append(Landfal_sum)
                stormNamesum.append(stormName)
                print("Storm Name :", stormName)
                dateRange.sort()
                print("Date Range :", prettify(dateRange[0]), "-", prettify(dateRange[-1]))
                if maximumSustainedWindSpeed != -1:
                    print("Maximum Sustained Wind Speed :", maximumSustainedWindSpeed)
                    print("Maximum Sustained Wind Date :", prettify(maximumSustainedWindDate))
                    print("Maximum Sustained Wind Time :",
                          maximumSustainedWindTime[:2] + ":" + maximumSustainedWindTime[
                                                               2:], "UTC")
                else:
                    print("Maximum Sustained Wind Speed : Not Available")
                print("Landfalls :", landFalls)

                stormInfo[stormYear] = stormInfo.get(stormYear, 0) + 1
                if isHurricane:
                    hurricaneInfo[stormYear] = hurricaneInfo.get(stormYear, 0) + 1

                # Initializing the global varibles for next storm
                dateRange = []
                maximumSustainedWindSpeed = -1
                maximumSustainedWindDate = ''
                maximumSustainedWindTime = ''
                landFalls = 0
                isHurricane = False
                print('-' * 40)
print('=' * 40)
print("Storm Statistics :")
for year in stormInfo:
    print("Year :", year)
    print("Storms :", stormInfo.get(year, 0))
    print("Hurricanes :", hurricaneInfo.get(year, 0))
    print("-" * 40)



# every block is a kind of storm, and in the block, there is a loop for all of the record i~[0,recordP_sum]
# all of blocks are in another loop j~[0,count]
# using latitude and longitude to calculate ev
# store all of the wind_distance in array wind_d
# store all of the latitude and longitude,time---two dimensional array

def wind_distance():
    wind_d = []
    wind_dper = []
    for j in range(count):
        try:
            Lat_sum1, Lont_sum1 = Lat_sums[j], Lont_sums[j]
            x = []
            x.append(ev.LatLon(Lat_sum1[0], Lont_sum1[0]))
            xs = []
            for i in range(recordP_sum[j] - 1):
                x.append(ev.LatLon(Lat_sum1[i + 1], Lont_sum1[i + 1]))
                xs.append(x[i + 1].distanceTo(x[i])/1852)
            wind_d.append(sum(xs))  # sum the distances for one storm and append them
            wind_dper.append(xs)  # append per distance between two points for every storm
        except Exception:
            wind_dper.append(0)
            wind_d.append(wind_d[-1])
    return [wind_d, wind_dper]


from datetime import datetime


def time_duration():
    time_d = []
    time_dper = []
    # print(time_sums)
    for j in range(count):
        Time = []
        for i in range(recordP_sum[j] - 1):
            startTime = datetime.strptime(time_sums[j][i], "%Y%m%d %H%M", )
            endTime = datetime.strptime(time_sums[j][i + 1], "%Y%m%d %H%M")
            TimeInteval = endTime - startTime
            Time.append(TimeInteval.total_seconds() / 3600)
            # print(Time)
        time_dper.append(Time)  # append per time durations for one storm
        time_d.append(sum(Time))  # append the sum of time durations for one storm
    return [time_d, time_dper]
    # print(time_dper,time_d)


# average speed= total distance(wind_d)/total time( time_d)
def get_avg(wind_d, time_d):
    speed_avg = []
    for j in range(count):
        try:
            speed_avg.append(wind_d[j]/time_d[j])
        except ZeroDivisionError:
            speed_avg.append(0)
    return speed_avg


# maximum speed for each knots
def get_avgknots(wind_dper, time_dper):
    maxspds=[]

    for j in range(count):
        try:
            maxspd = []
            for i in range(recordP_sum[j]-1):
                maxspd.append(wind_dper[j][i]/time_dper[j][i])
            maxspds.append(max(maxspd))
        except Exception:
            maxspds.append(0)
    return maxspds


# the degrees for all of the storms
def get_bearing():
    bear_sum=[]
    for j in range(count):
        Lat_sum1, Lont_sum1 = Lat_sums[j], Lont_sums[j]
        x=[]
        xs=[]
        x.append(ev.LatLon(Lat_sum1[0],Lont_sum1[0]))
        excep = x[0]
        for i in range(recordP_sum[j] - 1):
            # only one record or there are similar latitude and longitutude for two knots
            if recordP_sum[j]==1 or (Lat_sum1[i]==Lat_sum1[i+1] and Lont_sum1[i]==Lont_sum1[i+1]):
                x.append(0)
                xs.append(0)
            else:
                x.append(ev.LatLon(Lat_sum1[i+1],Lont_sum1[i+1]))
                try:
                    xs.append(excep.bearingTo(x[i+1]))
                except AttributeError:
                    print("there is something wrong here")
                excep = x[i+1]
        bear_sum.append(xs)
# find the previous one which is not 0.
    return bear_sum


# average degree for each knots of one storm
# maximum degree per unit time for each knots of one storm
def get_avgbearing(bear_sum, time_dper):
    avgbearings = []
    index=[]
    for j in range(count):
        try:
            indexi=[]
            avgbearing = []
            for i in range(recordP_sum[j]-1):
                avgbearing.append(bear_sum[j][i]/time_dper[j][i])
                indexi.append(max(range(len(avgbearing)),key=lambda x:avgbearing[x]))
            index.append(indexi)
            avgbearings.append(max(avgbearing))
        except (ZeroDivisionError,ValueError) as Exception:
            avgbearings.append(0)
    return [avgbearings,index]


# landfall percentage
def guesssuccess(index):
    truthcount=0
    falsecount=0
    guesspos=0.0
    for j in range(count):
        for i in range(recordP_sum[j]-1):
            # if the landfall occurs after the largest degree
            if len(Landfal_sums[j])>0 and Landfal_sums[j][0]>index[j][0]:
                falsecount+=1
            else:
                truthcount+=1
            guesspos=truthcount/(truthcount+falsecount)
    return guesspos


if __name__ == '__main__':
    with open('test.txt','wt')as f:
        wind_list=wind_distance()
        time_list = time_duration()
        bearinglist = get_avgbearing(get_bearing(), time_list[1])
        maxspd1=get_avgknots(wind_list[1], time_list[1])
        avgspd1=get_avg(wind_list[0], time_list[0])
        totaldis1=wind_list[0]
        maxdeg1=bearinglist[0]
        # print("for every storm, its accumulated distance is :",wind_list[0]) # total distance for each storm
        # print('='*100)
        # # average speed for each storm)
        # print("the average speed for each storm is:",get_avg(wind_list[0],time_list[0]))
        # print('='*100)
        # # average speed for knots in each storm
        # print("the maximum average speed for two knots is:",get_avgknots(wind_list[1],time_list[1]))
        # # average bearing for knots in each storm
        # print('='*100)
        # print("the maximum directional degree change is:",bearinglist[0])
        # print('='*100)
        for j in range(count):
            print("storm name:", stormNamesum[j],
                  "Maximum speed:",maxspd1[j],
                  "average speed:", avgspd1[j],
                  "total distance", totaldis1[j],
                  "maximum degree:", maxdeg1[j],
                  file=f)
        # successful guess
        print("successful guess is:",guesssuccess(bearinglist[1]),file=f)


# 'int' object has no attribute "bearingTo"
# max can not be used from generator to generator