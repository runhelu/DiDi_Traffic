import pandas as pd
import string

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
            #print(line)
            time = line[2]
            if(len(line) >= 6):
                street = line[5]
                if(not time in timeStreetMap):
                    list0 = [street]
                    timeStreetMap[time] = list0
                else:
                    timeStreetMap[time].append(street)

sortedTuples = sorted(timeStreetMap.items(),key=lambda x:x[0])

with open("timeStreet.csv", "a+", encoding="utf-8") as f:
    for singleTuple in sortedTuples:
        key = singleTuple[0]
        string = str(key)
        for street in singleTuple[1]:
            string += " " + street
        string += "\n"
        f.write(string)
