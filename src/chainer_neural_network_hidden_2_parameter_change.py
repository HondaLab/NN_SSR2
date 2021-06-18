import numpy as np
import matplotlib.pyplot as plt
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


file_name = os.path.basename('_parameter_change_Eta_hidden_2')
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
        

def net_train(hidden_number1,hidden_number2,EPOCH,STOP_ERROR,ALPHA,BETA1,BETA2,EPS,ETA,WEIGHT_RATE):
    
    have_epoch_number = 0
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
            have_epoch_number = i+1
            #print('break:',i)
            break
        if i == (epoch - 1):
            have_epoch_number = i+1
            #print('break:最大学習回数に至った',epoch)
            break
    #plt.plot(range(0,len(loss_list)),loss_list)
    #plt.show()
    return np.abs(loss),have_epoch_number
    #plt.scatter(1,loss_list)
    #plt.plot(xtrain,ytrain)
    

hidden_num1 = 700
hidden_num2 = 800
min_error_train = 999999
min_error_location_train_hidden1 = 0
min_error_location_train_hidden2 = 0
min_error_have_epoch_number = 0


Epoch=10000
Stop_Error=0.01
Alpha=0.001
Beta1=0.9
Beta2=0.999
Eps=1e-08
#Eta=1.0
Weight_Decay_Rate=0

change_Eta_list = np.linspace(0.001,1,500)
change_Eta_loss_list = np.zeros((1,len(change_Eta_list)))
have_epoch_list = np.zeros((1,len(change_Eta_list)))

ii = 0
pp = 0
start_time = time.time()
j = 0
for change_Eta in change_Eta_list:
    change_Eta_loss_list[0,j],have_epoch_list[0,j] = net_train(hidden_num1,hidden_num2,Epoch,Stop_Error,Alpha,Beta1,Beta2,Eps,change_Eta,Weight_Decay_Rate)
    if change_Eta_loss_list[0,j] < min_error_train:
        min_error_train = change_Eta_loss_list[0,j]
        min_error_location_train = change_Eta
        min_error_have_epoch_number = have_epoch_list[0,j]
    j = j + 1
end_time = time.time()  
second = end_time - start_time
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
    

print("min error : ",min_error_train)
print("location of min error : ",min_error_location_train)
print("have epoch number",min_error_have_epoch_number)

plt.figure(1)
plt.scatter(have_epoch_list[0,:],change_Eta_loss_list[0,:])
plt.xlabel("have_epoch_number")
plt.ylabel("error")
plt.savefig(folder+'/'+'ralation_epoch_error.pdf',bbox_inches='tight')
#plt.show()

plt.figure(2)
plt.plot(change_Eta_list,change_Eta_loss_list[0,:])
plt.xlabel("Eta value")
plt.ylabel("error")
plt.savefig(folder+'/'+'Eta_change_result_error.pdf',bbox_inches='tight')
#plt.show()

plt.figure(3)
plt.plot(change_Eta_list,have_epoch_list[0,:])
plt.xlabel("Eta value")
plt.ylabel("have epoch number")
plt.savefig(folder+'/'+'Eta_change_result_have_epoch_number.pdf',bbox_inches='tight')
#plt.show()


