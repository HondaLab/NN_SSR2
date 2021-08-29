#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain,cuda
import csv
import re
import os
import time
import pandas as pd

distance_data_num = 2
distance_data_weight = 5 
disdata_list = []
disdata_list.append(distance_data_num)
disdata_list.append(distance_data_weight)

f3 = open('disdata_num_weight.csv','w',encoding='utf-8')
csv_writer3 = csv.writer(f3)
csv_writer3.writerow(disdata_list)      
f3.close()

path1 = "chainer_data_in_include_distance_data.csv"
path2 = "chainer_motor_out.csv"

data_in = pd.read_csv(path1,header=None)
data_in = data_in.values
disdata_back3 = data_in[:,-3:]*distance_data_weight
data_in = data_in[:,0:960]
for di in range(0,distance_data_num):
    data_in = np.hstack((data_in,disdata_back3))
data_out = pd.read_csv(path2,header=None)
data_out = data_out.values

#print(data_in[0,:])
#print(data_in.shape)   #dataのサイズを出力してcheckしてください

xtrain = [[float(0) for i in range(int(data_in.shape[1]))] for j in range(data_in.shape[0])]   
ytrain = [[float(0) for i in range(int(data_out.shape[1]))] for j in range(data_out.shape[0])]
 
data_in_max_list = []
data_in_max = data_in.max()
for i in range(0,data_in.shape[1]):
    #data_in_max = data_in[:,i].max()
    data_in_max_list.append(data_in_max)
    #data_mean = data_in[:,i].mean()
    #data_stand = data_in[:,i].std()
    for v in range(0,data_in.shape[0]):
        xtrain[v][i] = data_in[v,i]/data_in_max
        #xtrain[v][i] =(data_in[v,i] - data_mean)/data_stand

data_out_max_list = []
data_out_max = data_out.max()

for i in range(0,data_out.shape[1]):
    #data_out_max = data_out[:,i].max()
    data_out_max_list.append(data_out_max)
    #data_mean = data_out[:,i].mean()
    #data_stand = data_out[:,i].std()
    for v in range(0,data_out.shape[0]):
        ytrain[v][i] = data_out[v,i]/data_out_max
        #ytrain[v][i] = (data_out[v,i] - data_mean)/data_stand
print("Train data number : ",data_out.shape[0])
        
f = open('Input_data_max.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
csv_writer.writerow(data_in_max_list)        
f.close()
f2 = open('Output_data_max.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
csv_writer2.writerow(data_out_max_list)      
f2.close()

def net_train(hidden_number,EPOCH,STOP_ERROR,ALPHA,BETA1,BETA2,EPS,ETA,WEIGHT_RATE):
    
    epoch = EPOCH    #学習回数
    INPUT_UNIT = data_in.shape[1]  #入力層のユニット
    HIDDEN_UNIT = hidden_number #中間層のユニット
    OUTPUT_UNIT = data_out.shape[1] #出力層のユニット

    class MyChain(Chain):
        def __init__(self):
            super(MyChain, self).__init__(
                l1=L.Linear(int(INPUT_UNIT),int(HIDDEN_UNIT)),
                l2=L.Linear(int(HIDDEN_UNIT),int(OUTPUT_UNIT)),
             )
        
        def fwd(self,x):
            h1 = F.relu(self.l1(x))
            h2 = self.l2(h1)
            return h2    

        def __call__(self, x, y):
            fv = self.fwd(x)
            loss = F.mean_squared_error(fv, y)
            return loss

    nn = MyChain()

    gpu_device = 0
    cuda.get_device(gpu_device).use()
    nn.to_gpu(gpu_device)
    xp = cuda.cupy
    x = Variable(xp.array(xtrain, dtype=xp.float32))
    y = Variable(xp.array(ytrain, dtype=xp.float32))

    optimizer = optimizers.Adam(alpha=ALPHA,beta1=BETA1,beta2=BETA2,eps=EPS,eta=ETA,weight_decay_rate=WEIGHT_RATE,amsgrad=False)
    optimizer.setup(nn)   

    loss_list = []
    loss_limit = STOP_ERROR
    loss_limit_flag = 0
    flag_limit = 100
    for i in range(0,epoch):
        nn.zerograds()
        loss = nn(x,y)
        loss.backward()
        optimizer.update()
    
        loss = re.sub('variable','',str(loss))
        loss = loss[1:-1]
        loss = float(loss)
        loss_list.append(loss)
    
        if len(loss_list) > 2:
            if np.abs(loss_list[-1] - loss_list[-2]) < loss_limit:
                loss_limit_flag = loss_limit_flag + 1
            if np.abs(loss_list[-1] - loss_list[-2]) > loss_limit:
                loss_limit_flag = 0
        if loss_limit_flag > flag_limit:
            file_name = 'optimum_weight_'+ str(hidden_number)
            serializers.save_npz(file_name, nn)
            #print('break:',i)
            break
        if i == (epoch - 1):
            file_name = 'optimum_weight_'+ str(hidden_number)
            serializers.save_npz(file_name, nn)
            #print('break:最大学習回数に至った',epoch)
            break
    #plt.plot(range(0,len(loss_list)),loss_list)
    return np.abs(loss)
    #plt.scatter(1,loss_list)
    #plt.plot(xtrain,ytrain)
    

"""read test file change to test value"""

with open('Input_data_max.csv','r') as f:
    reader = csv.reader(f)
    d = list(reader)
    d_in_max = d[0]   #is list
    
with open('Output_data_max.csv','r') as f2:
    reader2 = csv.reader(f2)
    d = list(reader2)
    d_out_max = d[0]#is list
     
Data_in_max = np.zeros((1,len(d_in_max)))
for i in range(0,len(d_in_max)):
    Data_in_max[0,i] = d_in_max[i]
Data_out_max = np.zeros((1,len(d_out_max)))
for i in range(0,len(d_out_max)):
    Data_out_max[0,i] = d_out_max[i]


#path1 = "prediction_data_in.csv"
#prediction_data_in = pd.read_csv(path1,header=None)
#prediction_data_in = prediction_data_in.values
prediction_data_in = data_in
#path2 = "prediction_data_out.csv"
prediction_data_out = pd.read_csv(path2,header=None)
prediction_data_out = prediction_data_out.values
#print(prediction_data_out.shape) #dataのサイズを出力してcheckしてください

for i in range(0,prediction_data_in.shape[1]):
    for v in range(0,prediction_data_in.shape[0]):
        prediction_data_in[v,i] = prediction_data_in[v,i]/Data_in_max[0,i]
#for i in range(0,prediction_data_out.shape[1]):
    #for v in range(0,prediction_data_out.shape[0]):
        #prediction_data_out[v,i] = prediction_data_out[v,i]/Data_out_max[0,i]

def net_test(HiddenNumber):
    INPUT_UNIT = prediction_data_in.shape[1]  #入力層のユニット
    HIDDEN_UNIT = HiddenNumber #中間層のユニット
    OUTPUT_UNIT = prediction_data_out.shape[1] #出力層のユニット
        
    class MyChain_test(Chain):
        def __init__(self):
            super(MyChain_test, self).__init__(
                l1=L.Linear(int(INPUT_UNIT),int(HIDDEN_UNIT)),
                l2=L.Linear(int(HIDDEN_UNIT),int(OUTPUT_UNIT)),
             )
        
        def fwd(self,x):
            h1 = F.relu(self.l1(x))
            h2 = self.l2(h1)
            return h2 
    
    nn_prediction = MyChain_test()
    file_name = 'optimum_weight_' + str(HIDDEN_UNIT)
    serializers.load_npz(file_name, nn_prediction)
    
    gpu_device = 0
    cuda.get_device(gpu_device).use()
    nn_prediction.to_gpu(gpu_device)
    xp2 = cuda.cupy
    
    y_out = np.zeros((prediction_data_out.shape[0],prediction_data_out.shape[1]))
    prediction_loss = []
    for i in range(0,prediction_data_in.shape[0]):
        x_in = [[]]
        for j in range(0,prediction_data_in.shape[1]):
            x_in[0].append(float(prediction_data_in[i][j]))
        x_in_train = Variable(xp2.array(x_in,dtype=np.float32))
        yy = nn_prediction.fwd(x_in_train)
        yy = re.sub('variable','',str(yy))
        yy = yy[3:-3]
        yy = yy.split()  #yy is a list
        for k in range(0,len(yy)):
            y_out[i,k] = float(yy[k])
            y_out[i,k] = y_out[i,k] * Data_out_max[0,k]
        #yy = [float(yy[0]),float(yy[1])]
        #y_out.append(float(yy[0]))
        l = y_out[i,:] - prediction_data_out[i,:]
        prediction_loss.append(np.mean(np.multiply(l,l)))
    #plt.plot(range(0,prediction_data_in.shape[0]),y_out[:,0])
    pred_error = np.mean(prediction_loss)
    return pred_error,y_out

figsize_x = 40
figsize_y = 10

hidden_num = range(1000,1001,10)
hidden_num_loss_train = np.zeros((1,len(hidden_num)))
min_error_train = 999999
min_error_location_train = 0

Epoch=7000
Stop_Error=0.0001
Alpha=0.001
Beta1=0.9
Beta2=0.999
Eps=1e-08
Eta=0.3
Weight_Decay_Rate=0

start_time = time.time()
j = 0
for i in hidden_num:
    hidden_num_loss_train[0,j] = net_train(i,Epoch,Stop_Error,Alpha,Beta1,Beta2,Eps,Eta,Weight_Decay_Rate)
    if hidden_num_loss_train[0,j] < min_error_train:
        min_error_train = hidden_num_loss_train[0,j]
        min_error_location_train = i
    j = j + 1  
out_error,output_data = net_test(min_error_location_train)  
end_time = time.time()  
loop1_time = end_time - start_time



hidden_num_loss_test = np.zeros((1,len(hidden_num)))
min_error_test = 99999
min_error_location_test = 0
min_error_output_test = np.zeros((prediction_data_out.shape[0],prediction_data_out.shape[1]))
j = 0
start_time = time.time()
for z in hidden_num:
    hidden_num_loss_test[0,j],output_data_test = net_test(z)
    if j == 0:
        min_error_test = hidden_num_loss_test[0,j]
        min_error_location_test = z
        min_error_output_test = output_data_test
    if hidden_num_loss_test[0,j] < min_error_test:
        min_error_test = hidden_num_loss_test[0,j]
        min_error_location_test = z
        min_error_output_test = output_data_test
    j = j + 1
end_time = time.time()
loop2_time = end_time-start_time

second = loop1_time + loop2_time
minute = 0
hour   = 0
while(second >= 60):
    second = second - 60
    minute = minute + 1
while(minute >= 60):
    minute = minute - 60
    hour   = hour   + 1
print("Spend Time : ")
print(str(hour) + ":"+str(minute) + ":" + str(np.floor(second)))

print("training finished")

"""
plt.figure(1)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.scatter(hidden_num,hidden_num_loss_train[0,:])
ax.plot(hidden_num,hidden_num_loss_train[0,:])
plt.xlabel("neuron number in hidden layer")
plt.ylabel("train data error with different neuron number in hidden layer")
plt.savefig('TrainError_Hidden.pdf',bbox_inches='tight')
#plt.show()

plt.figure(2)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(output_data[:,0],label='train')
ax.plot(prediction_data_out[:,0],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's left motor output of network based on train data's best weights and b ")
plt.savefig('TrainWeight_LeftOutput.pdf',bbox_inches='tight')
#plt.show()

plt.figure(3)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(output_data[:,1],label='train')
ax.plot(prediction_data_out[:,1],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's right motor output of network based on train data's best weights and b ")
plt.savefig('TrainWeight_rightOutput.pdf',bbox_inches='tight')
#plt.show()

plt.figure(4)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.scatter(hidden_num,hidden_num_loss_test[0,:])
ax.plot(hidden_num,hidden_num_loss_test[0,:])
plt.xlabel("neuron number in hidden layer")
plt.ylabel("test data error with different neuron number in hidden layer")
plt.savefig('TestError_Hidden.pdf',bbox_inches='tight')
#plt.show()

plt.figure(5)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(min_error_output_test[:,0],label='train')
ax.plot(prediction_data_out[:,0],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's left motor output of network based on test data's best weights and b ")
plt.savefig('TestWeight_leftOutput.pdf',bbox_inches='tight')
#plt.show()

plt.figure(6)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(min_error_output_test[:,1],label='train')
ax.plot(prediction_data_out[:,1],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's right motor output of network based on test data's best weights and b ")
plt.savefig('TestWeight_rightOutput.pdf',bbox_inches='tight')
#plt.show()


print("Output Error of Train Data : ",out_error)
print("The best hidden layer number of Train Data : ",min_error_location_train)
print("Output Error of Test Data : ",min_error_test)
print("The best hidden layer number of Test Data : ",min_error_location_test)
"""
