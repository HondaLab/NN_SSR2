import numpy as np
import matplotlib.pyplot as plt
#from pandas_ods_reader import read_ods
import csv
import re
import pandas as pd
import os

folder_num = 9

f = open('interdration_data_two_dimension/chainer_motor_out.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       

picture_num = 0

folder_num_list = os.listdir("data_two_dimension/")
print(folder_num_list)

for i in folder_num_list:
    folder = "data_two_dimension/" + str(i)
    path = folder + "/opencv_data_out"
    data = pd.read_csv(path)
    data = data.values
    print(data.shape[0])
    picture_num = picture_num + data.shape[0]
    
    for j in range(0,data.shape[0]):
        csv_writer.writerow(data[j,:])        
f.close()
print("the number of picture : ",picture_num)


for num in range(1,4,1):
    f1 = open('chainer_data_in'+str(num)+'.csv','w',encoding='utf-8')
    csv_writer = csv.writer(f1) 
    csv_writer.writerow("M")

    for i in folder_num_list:
        folder = "data_two_dimension/" + str(i)
        path1 = folder + "/opencv_data_in"+str(num)
        data1 = pd.read_csv(path1)
        data1 = data1.values
        print(data1.shape[0])
        for j in range(0,data1.shape[0]):
            csv_writer.writerow(data1[j,:])        
    f1.close()

path1 = "chainer_data_in1.csv"
path2 = "chainer_data_in2.csv"
path3 = "chainer_data_in3.csv"

data1 = pd.read_csv(path1)
data1 = data1.values
data2 = pd.read_csv(path2)
data2 = data2.values
data3 = pd.read_csv(path3)
data3 = data3.values

print("the shape of data in 1",data1.shape)
print("the shape of data in 2",data2.shape)
print("the shape of data in 3",data3.shape)


data_in1 = np.zeros((data1.shape[0],320))
data_in2 = np.zeros((data2.shape[0],320))
data_in3 = np.zeros((data3.shape[0],320))
for u in range(0,data1.shape[0]):
    if data1[u,0] != "MMM":
        a = data1[u,0]
        b = a.split("\t")
        for v in range(0,320):
            data_in1[u,v] = b[v]
            
        a = data2[u,0]
        b = a.split("\t")
        for v in range(0,320):
            data_in2[u,v] = b[v]
            
        a = data3[u,0]
        b = a.split("\t")
        for v in range(0,320):
            data_in3[u,v] = b[v]
            
    else:
        data_in1[u,0] = -333
        data_in2[u,0] = -333
        data_in3[u,0] = -333
        
#del data1 data2 data3

image = np.zeros((320,320,3))
for i in range(0,320):
    image[i,:,1] = data_in1[i,:]
    image[i,:,2] = data_in2[i,:]
    image[i,:,0] = data_in3[i,:]
plt.imshow(image)



limit_top = 167
limit_below = 235
image = np.zeros((limit_below-limit_top,320,3))
for i in range(limit_top,limit_below,1):
    image[i-limit_top,:,1] = data_in1[i,:]
    image[i-limit_top,:,2] = data_in2[i,:]
    image[i-limit_top,:,0] = data_in3[i,:]
plt.imshow(image)

cut_data_in1 = np.zeros((limit_below-limit_top,320,picture_num))
cut_data_in2 = np.zeros((limit_below-limit_top,320,picture_num))
cut_data_in3 = np.zeros((limit_below-limit_top,320,picture_num))
flag = -1
flag2 = -1
pic_num = 0
for k in range(0,data_in1.shape[0]):
    if data_in1[k,0] == -333:
        flag = -1
        flag2 = k
        pic_num = pic_num + 1
    else:
        flag = flag + 1
        flag2 = flag2 + 1
        
    if flag >= limit_top and flag < limit_below:
        cut_data_in1[flag-limit_top,:,pic_num] = data_in1[flag2,:]
        cut_data_in2[flag-limit_top,:,pic_num] = data_in2[flag2,:]
        cut_data_in3[flag-limit_top,:,pic_num] = data_in3[flag2,:]
        
print("the shape of cut data in 1",cut_data_in1.shape)

image2 = np.zeros((limit_below-limit_top,320,3))
loc = 67
image2[:,:,1] = cut_data_in1[:,:,loc]
image2[:,:,2] = cut_data_in2[:,:,loc]
image2[:,:,0] = cut_data_in3[:,:,loc]
plt.imshow(image2)


"""
f2 = open('chainer_data_in.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
input_data = np.zeros((cut_data_in1.shape[2],cut_data_in1.shape[1]))
for h in range(0,cut_data_in1.shape[2]):
    for k in range(0,cut_data_in1.shape[1]):
        input_data[h,k] = sum(cut_data_in1[:,k,h]) + sum(cut_data_in2[:,k,h]) + sum(cut_data_in3[:,k,h])
    csv_writer2.writerow(input_data[h,:])
f2.close()
"""

f2 = open('interdration_data_two_dimension/chainer_data_in.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
input_data = np.zeros((cut_data_in1.shape[2],cut_data_in1.shape[1]*2))
input_data2 = np.zeros((cut_data_in1.shape[2],cut_data_in1.shape[1]*3))
Blue = np.zeros((1,cut_data_in1.shape[1]))
Green = np.zeros((1,cut_data_in1.shape[1]))
Red = np.zeros((1,cut_data_in1.shape[1]))
for h in range(0,cut_data_in1.shape[2]):
    for k in range(0,cut_data_in1.shape[1]):
        Blue[0,k] = sum(cut_data_in1[:,k,h])
        Green[0,k] = sum(cut_data_in2[:,k,h])
        Red[0,k] = sum(cut_data_in3[:,k,h])
    input_data[h,:] = np.append(Blue[0,:],Green[0,:])
    input_data2[h,:] = np.append(input_data[h,:],Red[0,:])
    csv_writer2.writerow(input_data2[h,:])
f2.close()

os.remove("chainer_data_in1.csv")
os.remove("chainer_data_in2.csv")
os.remove("chainer_data_in3.csv")

print("the shape of final data in : ",input_data2.shape)

        

