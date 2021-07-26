import numpy as np
import matplotlib.pyplot as plt
#from pandas_ods_reader import read_ods
import csv
import re
import pandas as pd
import os    

f = open('interdration_data_one_dimension/chainer_motor_out.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
f2 = open('interdration_data_one_dimension/chainer_data_in.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2) 

picture_num = 0
folder_num_list = os.listdir("data_one_dimension/")
print(folder_num_list)

for i in folder_num_list:
    folder = "data_one_dimension/" + str(i)
    path = folder + "/chainer_motor_out.csv"
    path2 = folder + "/chainer_data_in.csv"
    data = pd.read_csv(path)
    data2 = pd.read_csv(path2)
    data = data.values
    data2 = data2.values
    print("folder"+str(i)+" : ",data.shape[0],",",data2.shape[0])
    picture_num = picture_num + data.shape[0]
    
    for j in range(0,data.shape[0]):
        csv_writer.writerow(data[j,:]) 
        csv_writer2.writerow(data2[j,:])       
f.close()
f2.close()
print("the number of picture : ",picture_num)



        

