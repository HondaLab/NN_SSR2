import numpy as np
import matplotlib.pyplot as plt
#from pandas_ods_reader import read_ods
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain, cuda
import csv
import re
import os
import time
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D


file_name = os.path.basename('_chainer_neural_network_hidden_change_hidden_number_2')
folder = 'output' + file_name
if not os.path.exists(folder):
    os.mkdir(folder)


path1 = "chainer_data_in.csv"
path2 = "chainer_motor_out.csv"

data_in = pd.read_csv(path1)
data_in = data_in.values
data_out = pd.read_csv(path2)
data_out = data_out.values

xtrain = [[float(0) for i in range(int(data_in.shape[1]))] for j in range(data_in.shape[0])]   
ytrain = [[float(0) for i in range(int(data_out.shape[1]))] for j in range(data_out.shape[0])]
#print(data_in.shape[1])
 
data_in_max_list = []
data_in_max = data_in.max()
for i in range(0,data_in.shape[1]):
    data_in_max_list.append(data_in_max)
    #data_mean = data_in[:,i].mean()
    #data_stand = data_in[:,i].std()
    for v in range(0,data_in.shape[0]):
        xtrain[v][i] = data_in[v,i]/data_in_max
        #xtrain[v][i] =(data_in[v,i] - data_mean)/data_stand
#print(data_in.shape)
data_out_max_list = []
data_out_max = data_out.max()
for i in range(0,data_out.shape[1]):
    data_out_max_list.append(data_out_max)
    #data_mean = data_out[:,i].mean()
    #data_stand = data_out[:,i].std()
    for v in range(0,data_out.shape[0]):
        ytrain[v][i] = data_out[v,i]/data_out_max
        #data_out[v,i] = (data_out[v,i] - data_mean)/data_stand
        
f = open(folder+'/'+'data_in_max.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
csv_writer.writerow(data_in_max_list)        
f.close()
f2 = open(folder+'/'+'data_out_max.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
csv_writer2.writerow(data_out_max_list)      
f2.close()

def net_train(hidden_number1,hidden_number2,EPOCH,STOP_ERROR,ALPHA,BETA1,BETA2,EPS,ETA,WEIGHT_RATE):
    
    epoch = EPOCH    #学習回数
    INPUT_UNIT = data_in.shape[1]  #入力層のユニット
    HIDDEN_UNIT_1 = hidden_number1 #中間層1のユニット
    HIDDEN_UNIT_2 = hidden_number2 #中間層2のユニット
    OUTPUT_UNIT = data_out.shape[1] #出力層のユニット

    class MyChain(Chain):
        def __init__(self):
            super(MyChain, self).__init__(
                l1=L.Linear(int(INPUT_UNIT),int(HIDDEN_UNIT_1)),
                l2=L.Linear(int(HIDDEN_UNIT_1),int(HIDDEN_UNIT_2)),
                l3=L.Linear(int(HIDDEN_UNIT_2),int(OUTPUT_UNIT)),
             )
        
        def fwd(self,x):
            h1 = F.relu(self.l1(x))
            h2 = F.relu(self.l2(h1))
            h3 = self.l3(h2)
            return h3 

        def __call__(self, x, y):
            fv = self.fwd(x)
            loss = F.mean_squared_error(fv, y)
            return loss

    nn = MyChain()
    optimizer = optimizers.Adam(alpha=ALPHA,beta1=BETA1,beta2=BETA2,eps=EPS,eta=ETA,weight_decay_rate=WEIGHT_RATE,amsgrad=False)
    optimizer.setup(nn)
    
    gpu_device = 0
    cuda.get_device(gpu_device).use()
    nn.to_gpu(gpu_device)
    xp = cuda.cupy
    
    x = Variable(xp.array(xtrain, dtype=xp.float32))
    y = Variable(xp.array(ytrain, dtype=xp.float32))
    
    
    #x = Variable(np.array(xtrain, dtype=np.float32))
    #y = Variable(np.array(ytrain, dtype=np.float32))

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
    
        if np.abs(loss) < loss_limit:
            loss_limit_flag = loss_limit_flag + 1
        if loss_limit_flag > flag_limit:
            file_name = 'optimum_weight_'+ str(hidden_number1)+ "_" + str(hidden_number2)
            serializers.save_npz(folder + '/' + file_name, nn)
            #print('break:',i)
            break
        if i == (epoch - 1):
            file_name = 'optimum_weight_'+ str(hidden_number1)+ "_" + str(hidden_number2)
            serializers.save_npz(folder + '/' + file_name, nn)
            #print('break:最大学習回数に至った',epoch)
            break
    #plt.plot(range(0,len(loss_list)),loss_list)
    #plt.show()
    return np.abs(loss)
    #plt.scatter(1,loss_list)
    #plt.plot(xtrain,ytrain)
    

"""read test file change to test value"""

with open(folder+'/'+'data_in_max.csv','r') as f:
    reader = csv.reader(f)
    d = list(reader)
    d_in_max = d[0]   #is list
    
with open(folder+'/'+'data_out_max.csv','r') as f2:
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
prediction_data_in = pd.read_csv(path1)
prediction_data_in = prediction_data_in.values
#path2 = "prediction_data_out.csv"
prediction_data_out = pd.read_csv(path2)
prediction_data_out = prediction_data_out.values

for i in range(0,prediction_data_in.shape[1]):
    for v in range(0,prediction_data_in.shape[0]):
        prediction_data_in[v,i] = prediction_data_in[v,i]/Data_in_max[0,i]
#for i in range(0,prediction_data_out.shape[1]):
    #for v in range(0,prediction_data_out.shape[0]):
        #prediction_data_out[v,i] = prediction_data_out[v,i]/Data_out_max[0,i]
        
def net_test(HiddenNumber_1,HiddenNumber_2):
    INPUT_UNIT = prediction_data_in.shape[1]  #入力層のユニット
    HIDDEN_UNIT_1 = HiddenNumber_1 #中間層のユニット
    HIDDEN_UNIT_2 = HiddenNumber_2 #中間層のユニット
    OUTPUT_UNIT = prediction_data_out.shape[1] #出力層のユニット
        
    class MyChain_test(Chain):
        def __init__(self):
            super(MyChain_test, self).__init__(
                l1=L.Linear(int(INPUT_UNIT),int(HIDDEN_UNIT_1)),
                l2=L.Linear(int(HIDDEN_UNIT_1),int(HIDDEN_UNIT_2)),
                l3=L.Linear(int(HIDDEN_UNIT_2),int(OUTPUT_UNIT)),
             )
        
        def fwd(self,x):
            h1 = F.relu(self.l1(x))
            h2 = F.relu(self.l2(h1))
            h3 = self.l3(h2)
            return h3
    
    nn_prediction = MyChain_test()
    
    gpu_device = 0
    cuda.get_device(gpu_device).use()
    nn_prediction.to_gpu(gpu_device)
    xp2 = cuda.cupy
    
    file_name = 'optimum_weight_' + str(HIDDEN_UNIT_1)+ "_" + str(HIDDEN_UNIT_2)
    serializers.load_npz(folder + '/' + file_name, nn_prediction)

    #y_out = []
    y_out = np.zeros((prediction_data_out.shape[0],prediction_data_out.shape[1]))
    prediction_loss = []
    for i in range(0,prediction_data_in.shape[0]):
        x_in = [[]]
        for j in range(0,prediction_data_in.shape[1]):
            x_in[0].append(float(prediction_data_in[i][j]))
        x_in_train = Variable(xp2.array(x_in,dtype=xp2.float32))
        #x_in_train = Variable(np.array(x_in,dtype=np.float32))
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


hidden_num1 = range(300,1100,20)
hidden_num2 = range(300,1100,20)
hidden_num_loss_train = np.zeros((len(hidden_num1),len(hidden_num2)))
min_error_train = 999999
min_error_location_train_hidden1 = 0
min_error_location_train_hidden2 = 0

Epoch=10000
Stop_Error=0.01
Alpha=0.001
Beta1=0.9
Beta2=0.999
Eps=1e-08
Eta=0.3
Weight_Decay_Rate=0

ii = 0
pp = 0
start_time = time.time()
for i in hidden_num1:
    for p in hidden_num2:
        hidden_num_loss_train[ii,pp] = net_train(i,p,Epoch,Stop_Error,Alpha,Beta1,Beta2,Eps,Eta,Weight_Decay_Rate)
        if hidden_num_loss_train[ii,pp] < min_error_train:
            min_error_train = hidden_num_loss_train[ii,pp]
            min_error_location_train_hidden1 = i
            min_error_location_train_hidden2 = p
        pp =pp + 1
    ii = ii + 1
    pp = 0
out_error,output_data = net_test(min_error_location_train_hidden1,min_error_location_train_hidden2)  
end_time = time.time()  
loop1_time = end_time - start_time

hidden_num_loss_test = np.zeros((len(hidden_num1),len(hidden_num2)))
min_error_test = 99999
min_error_location_test_hidden1 = 0
min_error_location_test_hidden2 = 0
min_error_output_test = np.zeros((prediction_data_out.shape[0],prediction_data_out.shape[1]))
zz = 0
kk = 0
start_time = time.time()
for z in hidden_num1:
    for k in hidden_num2:
        hidden_num_loss_test[zz,kk],output_data_test = net_test(z,k)
        if zz == 0:
            min_error_test = hidden_num_loss_test[zz,kk]
            min_error_location_test_hidden1 = z
            min_error_location_test_hidden2 = k
            min_error_output_test = output_data_test
        if hidden_num_loss_test[zz,kk] < min_error_test:
            min_error_test = hidden_num_loss_test[zz,kk]
            min_error_location_test_hidden1 = z
            min_error_location_test_hidden2 = k
            min_error_output_test = output_data_test
        kk = kk + 1
    zz = zz + 1
    kk = 0
    
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
print(str(hour) + ":"+str(minute) + ":" + str(second))
    



figsize_x = 15
figsize_y = 10

figsize_x_2 = 40
figsize_y_2 = 10

plt.figure(1)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax3 = plt.axes(projection='3d')
X,Y = np.meshgrid(hidden_num1,hidden_num2)
Z = hidden_num_loss_train
ax3.plot_surface(X,Y,Z,cmap='rainbow')
plt.xlabel("neuron number in hidden layer")
plt.ylabel("train data error with different neuron number in hidden layer")
plt.savefig(folder+'/'+'TrainError_Hidden_hidden_2.pdf',bbox_inches='tight')
#plt.show()



plt.figure(2)
fig = plt.figure(figsize=(figsize_x_2,figsize_y_2))
ax = fig.add_subplot(111)
ax.plot(output_data[:,0],label='train')
ax.plot(prediction_data_out[:,0],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's left motor output of network based on train data's best weights and b ")
plt.savefig(folder+'/'+'TrainWeight_LeftOutput_hidden_2.pdf',bbox_inches='tight')
#plt.show()

plt.figure(3)
fig = plt.figure(figsize=(figsize_x_2,figsize_y_2))
ax = fig.add_subplot(111)
ax.plot(output_data[:,1],label='train')
ax.plot(prediction_data_out[:,1],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's right motor output of network based on train data's best weights and b ")
plt.savefig(folder+'/'+'TrainWeight_rightOutput_hidden_2.pdf',bbox_inches='tight')
#plt.show()




plt.figure(4)
fig = plt.figure(figsize=(figsize_x,figsize_y))
#ax3 = fig.add_subplot(111)
ax3 = plt.axes(projection='3d')
X,Y = np.meshgrid(hidden_num1,hidden_num2)
Z = hidden_num_loss_test
ax3.plot_surface(X,Y,Z,cmap='rainbow')
plt.xlabel("neuron number in hidden layer")
plt.ylabel("test data error with different neuron number in hidden layer")
plt.savefig(folder+'/'+'TestError_Hidden_hidden_2.pdf',bbox_inches='tight')
#plt.show()




plt.figure(5)
fig = plt.figure(figsize=(figsize_x_2,figsize_y_2))
ax = fig.add_subplot(111)
ax.plot(min_error_output_test[:,0],label='train')
ax.plot(prediction_data_out[:,0],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's left motor output of network based on test data's best weights and b ")
plt.savefig(folder+'/'+'TestWeight_leftOutput_hidden_2.pdf',bbox_inches='tight')
#plt.show()

plt.figure(6)
fig = plt.figure(figsize=(figsize_x_2,figsize_y_2))
ax = fig.add_subplot(111)
ax.plot(min_error_output_test[:,1],label='train')
ax.plot(prediction_data_out[:,1],label='teacher')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Test data's right motor output of network based on test data's best weights and b ")
plt.savefig(folder+'/'+'TestWeight_rightOutput_hidden_2.pdf',bbox_inches='tight')
#plt.show()

print("Output Error of Train Data : ",out_error)
print("The best hidden layer number of Train Data : ","hidden1 : ",min_error_location_train_hidden1,",","hidden2 : ",min_error_location_train_hidden2)
print("Output Error of Test Data : ",min_error_test)
print("The best hidden layer number of Test Data : ","hidden1 : ",min_error_location_test_hidden1,",","hidden2 : ",min_error_location_test_hidden2)
