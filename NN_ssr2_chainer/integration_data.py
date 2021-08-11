#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import pandas as pd
import os 

f = open('chainer_motor_out.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
f2 = open('chainer_data_in.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2) 
f3 = open('chainer_data_in_include_distance_data.csv','w',encoding='utf-8')
csv_writer3 = csv.writer(f3) 

end_data_name = input("Please input the quantity number of integrate data : ") 
picture_num = 0  

for i in range(1,int(end_data_name)+1):
    path = "part_motor_out"+str(i)+".csv"
    path2 = "part_data_in"+str(i)+".csv"
    path3 = "part_data_in_include_distance_data"+str(i)+".csv"
    data = pd.read_csv(path,header=None)
    data2 = pd.read_csv(path2,header=None)
    data3 = pd.read_csv(path3,header=None)
    data = data.values
    data2 = data2.values
    data3 = data3.values
    picture_num = picture_num + data.shape[0]
    for j in range(0,data.shape[0]):
        csv_writer.writerow(data[j,:]) 
        csv_writer2.writerow(data2[j,:])  
        csv_writer3.writerow(data3[j,:])      
f.close()
f2.close()
f3.close()
print("the number of picture : ",picture_num)



        

