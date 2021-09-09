#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import pandas as pd
import os

f = open('CNN_motor_out.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       

picture_num = 0
folder_start = input("Please input the start number of folder : ")
end_folder = input("Please input the end number of folder : ")
folder_num = range(int(folder_start),int(end_folder)+1,1)

for i in folder_num:
    folder = str(i)
    path = folder + "/opencv_data_out.csv"
    data = pd.read_csv(path)
    data = data.values
    #print(data.shape)
    picture_num = picture_num + data.shape[0]
    for j in range(0,data.shape[0]):
        dd = data[j,0].split("\t")
        csv_writer.writerow(dd) 
f.close()
"""
print("the number of picture : ",picture_num)
d_out = pd.read_csv('CNN_motor_out.csv',header=None).values
print(d_out.shape)
"""
for num in range(1,4,1):
    f0 = open('CNN_data_in'+str(num)+'.csv','w',encoding='utf-8')
    csv_writer0 = csv.writer(f0) 
    csv_writer0.writerow("M")

    for i in folder_num:
        folder = str(i)
        path0 = folder + "/opencv_data_in"+str(num)+".csv"
        data0 = pd.read_csv(path0)
        data0 = data0.values
        #print(data1.shape[0]/71)
        for j in range(0,data0.shape[0]):
            csv_writer0.writerow(data0[j,:])        
    f0.close()

data4 = pd.read_csv(path4,header=None)
data4 = data4.values
print("data out number :",int(data4.shape[0]))

"""
image_cut_size = 65
path1 = "CNN_data_in1.csv"
path2 = "CNN_data_in2.csv"
path3 = "CNN_data_in3.csv"
path4 = "CNN_motor_out.csv"
data1 = pd.read_csv(path1)
data1 = data1.values
data2 = pd.read_csv(path2)
data2 = data2.values
data3 = pd.read_csv(path3)
data3 = data3.values
print("data in 1 number :",int(data1.shape[0]/image_cut_size))
print("data in 2 number :",int(data2.shape[0]/image_cut_size))
print("data in 3 number :",int(data3.shape[0]/image_cut_size))
"""

