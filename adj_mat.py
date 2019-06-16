import pandas as pd
import string
import os

table = dict()
with open("timeStreet.csv", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip()
        line = line.split(" ")
        
        for i in range(1, len(line)):
            street = line[i]
            #print(street)
            if(street not in table):
                table[street] = 1
f.close()
if(os.path.exists("adj_matrix.csv")):
    os.remove("adj_matrix.csv")
    
with open("adj_matrix.csv", "a+", encoding="utf-8") as f:
    
    for key in table:
        string = key
        string += "\n"
        f.write(string)