import pandas as pd
import string
import sys
import os

timeStreetMap = dict()
with open("cache_0_10000.csv", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip()
        line = line.split(" ")
        #print(line)
        time = line[2]
        #print(time)
        street = line[5]
        if(not time in timeStreetMap):
            list0 = [street]
            timeStreetMap[time] = list0
        else:
            timeStreetMap[time].append(street)
f.close()

with open("cache_10000_30000.csv", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip()
        line = line.split(" ")
        #print(line)
        time = line[2]
        if(len(line) >= 6):
            street = line[5]
            if(not time in timeStreetMap):
                list0 = [street]
                timeStreetMap[time] = list0
            else:
                timeStreetMap[time].append(street)


for i in range(30000, 90000, 10000):            
    with open("cache_{}_{}.csv".format(i, i+10000), "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(" ")
            time = line[2]
            if(len(line) >= 6):
                street = line[5]
                if(not time in timeStreetMap):
                    list0 = [street]
                    timeStreetMap[time] = list0
                else:
                    timeStreetMap[time].append(street)

sortedTuples = sorted(timeStreetMap.items(),key=lambda x:x[0])

minValue = int(sortedTuples[0][0])
maxValue = int(sortedTuples[len(sortedTuples)-1][0])
print(minValue)
print(maxValue)
minMap = dict()

lastKey = minValue
for singleTuple in sortedTuples:
    key = singleTuple[0]
    if(int(key) < lastKey + 60):
        if lastKey in minMap:
            for street in singleTuple[1]:
                minMap[lastKey].append(street)
        else:
            minMap[lastKey] = []
            for street in singleTuple[1]:
                minMap[lastKey].append(street)
    else:
        lastKey = int(key)
        if lastKey in minMap:
            for street in singleTuple[1]:
                minMap[lastKey].append(street)
        else:
            minMap[lastKey] = []
            for street in singleTuple[1]:
                minMap[lastKey].append(street)

sortedTuples = sorted(minMap.items(),key=lambda x:x[0])

if(os.path.exists("timeStreet.csv")):
    os.remove("timeStreet.csv")
    
with open("timeStreet.csv", "a+", encoding="utf-8") as f:
    for singleTuple in sortedTuples:
        key = singleTuple[0]
        string = str(key)
        for street in singleTuple[1]:
            string += " " + street
        string += "\n"
        f.write(string)



        