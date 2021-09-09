#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain, cuda
import csv
import math
import re
import os
import time
import pandas as pd
import random

start_time = time.time()

path1 = "CNN_data_in1.csv"
path2 = "CNN_data_in2.csv"
path3 = "CNN_data_in3.csv"

data1 = pd.read_csv(path1)
data1 = data1.values
data2 = pd.read_csv(path2)
data2 = data2.values
data3 = pd.read_csv(path3)
data3 = data3.values
#print(data1.shape)

img_cut_size = 0
for f in range(0,data1.shape[0]):
    if data1[f,0] != "M":
        img_cut_size = img_cut_size+1
    else:
        break

limit_top = 0
limit_below = img_cut_size
print("Image cut size : ",img_cut_size)

BGR = 3
y_size = 320
liner_in_num = 2860
picture_number_cut = 800
Spatial_dim = 2
Image_channel_number = 3
Cn1_filter_number = 20
Cn1_filter_size_x = 3
Cn1_filter_size_y = 20
Cn1_stride = 2
Cn1_padding = 0
Cn2_filter_number = 50
Cn2_filter_size_x = 5
Cn2_filter_size_y = 12
Cn2_stride = 1
Cn2_padding = 0
Cn1_pooling_size_x = 3
Cn1_pooling_size_y = 12
Cn2_pooling_size_x = 3
Cn2_pooling_size_y = 12
Hiddle_number = 3000
Epoch = 1000
STOP_ERROR = 0.001
Dropout_pramater = 0.5

file_name = os.path.basename('_chainer_neural_network_hidden_change')
folder = 'output' + file_name
if not os.path.exists(folder):
    os.mkdir(folder)

path2 = "CNN_motor_out.csv"
data_out = pd.read_csv(path2,header=None)
data_out = data_out.values
#print(data_out.shape)
ytrain = np.zeros((data_out.shape[0],data_out.shape[1]))
for u in range(0,data_out.shape[0]):
    for v in range(0,data_out.shape[1]):
        ytrain[u,v] = data_out[u,v]

data_out_max_list = []
for i in range(0,data_out.shape[1]):
    data_out_max = data_out[:,i].max()
    data_out_max_list.append(data_out_max)
    for v in range(0,data_out.shape[0]):
        ytrain[v][i] = int(data_out[v,i])/int(data_out_max)
        
f2 = open(folder+'/'+'data_out_max.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
csv_writer2.writerow(data_out_max_list)      
f2.close()

picture_number = ytrain.shape[0]

xtrain = np.zeros((picture_number,BGR,limit_below-limit_top,y_size))
flag = -1
flag2 = -1
pic_num = 0

data_in1 = np.zeros((data1.shape[0],320))
data_in2 = np.zeros((data2.shape[0],320))
data_in3 = np.zeros((data3.shape[0],320))
for u in range(0,data1.shape[0]):
    if data1[u,0] != "M":
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
            
        flag = flag + 1
        flag2 = flag2 + 1
            
    else:
        flag = -1
        flag2 = u
        pic_num = pic_num + 1
        
    if flag >= limit_top and flag < limit_below:
        xtrain[pic_num,0,flag-limit_top,:] = data_in1[flag2,:]
        xtrain[pic_num,1,flag-limit_top,:] = data_in2[flag2,:]
        xtrain[pic_num,2,flag-limit_top,:] = data_in3[flag2,:]

print("picture number : ",pic_num)
del data1,data2,data3,data_in1,data_in2,data_in3
        
data_in_max_list = [xtrain[:,0,:,:].max(),xtrain[:,1,:,:].max(),xtrain[:,2,:,:].max()]
for i in range(0,picture_number):
    for j in range(0,BGR):
        for k in range(0,xtrain.shape[2]):
            for v in range(0,xtrain.shape[3]):
                xtrain[i,j,k,v] = xtrain[i,j,k,v]/data_in_max_list[j]
        
f = open(folder+'/'+'data_in_max.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
csv_writer.writerow(data_in_max_list)        
f.close()   

end_time = time.time()
second = end_time-start_time
minute = 0
hour   = 0
while(second >= 60):
    second = second - 60
    minute = minute + 1
while(minute >= 60):
    minute = minute - 60
    hour   = hour   + 1
print("Data reading Time : ",str(hour) + ":"+str(minute) + ":" + str(second))


def CNN_Train(pic_num_cut,input_data,output_data,picture_number,
              spatial_dim,image_channel_number,image_size_x,image_size_y,
              cn1_filter_number,cn1_filter_size_x,cn1_filter_size_y,cn1_stride,cn1_padding,
              cn2_filter_number,cn2_filter_size_x,cn2_filter_size_y,cn2_stride,cn2_padding,
              cn1_pooling_size_x,cn1_pooling_size_y,
              cn2_pooling_size_x,cn2_pooling_size_y,
              hiddle_number,output_number,epoch,STOP_ERROR,dropout_pramater):
    
    """
    lx1 = math.ceil((image_size_x-cn1_filter_size_x)/cn1_stride)+1
    lx2 = math.ceil(lx1/cn1_pooling_size_x)
    lx3 = math.ceil((lx2-cn2_filter_size_x)/cn2_stride)+1
    lx4 = math.ceil(lx3/cn2_pooling_size_x)
    ly1 = math.ceil((image_size_y-cn1_filter_size_y)/cn1_stride)+1
    ly2 = math.ceil(ly1/cn1_pooling_size_y)
    ly3 = math.ceil((ly2-cn2_filter_size_y)/cn2_stride)+1
    ly4 = math.ceil(ly3/cn2_pooling_size_y)
    l1_no_1_paramater = int(cn2_filter_number*ly4*lx4)
    #print(l1_no_1_paramater)
   
    
    class MyCNN(Chain):
        def __init__(self):
            super(MyCNN,self).__init__(
                cn1 = L.ConvolutionND(spatial_dim,image_channel_number,cn1_filter_number,(cn1_filter_size_x,cn1_filter_size_y),
                                      cn1_stride,cn1_padding),
                cn2 = L.ConvolutionND(spatial_dim,cn1_filter_number,cn2_filter_number,(cn2_filter_size_x,cn2_filter_size_y),
                                      cn2_stride,cn2_padding),
                l1 = L.Linear(l1_no_1_paramater,hiddle_number),
                l2 = L.Linear(hiddle_number,output_number),
            )
        def fwd(self,x):
            h1 = F.max_pooling_nd(F.relu(self.cn1(x)),(cn1_pooling_size_x,cn1_pooling_size_y))
            h2 = F.max_pooling_nd(F.relu(self.cn2(h1)),(cn2_pooling_size_x,cn2_pooling_size_y))
            h3 = F.dropout(F.relu(self.l1(h2)),dropout_pramater)
            out_layer = self.l2(h3)
            return out_layer
        
        def __call__(self,x,y):
            fv = self.fwd(x)
            loss = F.softmax_cross_entropy(fv,y)
            #loss = F.mean_squared_error(fv, y)
            return loss
        
    """
    class MyCNN(Chain):
        def __init__(self):
            super(MyCNN,self).__init__(
                cn1 = L.ConvolutionND(spatial_dim,image_channel_number,cn1_filter_number,(cn1_filter_size_x,cn1_filter_size_y),
                                      cn1_stride,cn1_padding),
                l1 = L.Linear(liner_in_num,hiddle_number),
                l2 = L.Linear(hiddle_number,output_number),
            )
        def fwd(self,x):
            h1 = F.max_pooling_nd(F.relu(self.cn1(x)),(cn1_pooling_size_x,cn1_pooling_size_y))
            h2 = F.dropout(F.relu(self.l1(h1)),dropout_pramater)
            out_layer = self.l2(h2)
            return out_layer
        
        def __call__(self,x,y):
            fv = self.fwd(x)
            loss = F.softmax_cross_entropy(fv,y)
            #loss = F.mean_squared_error(fv, y)
            return loss


    CNNmodel = MyCNN()
    optimizer = optimizers.Adam(alpha=0.001,beta1=0.9,beta2=0.999,eps=1e-08,eta=0.3,weight_decay_rate=0.7,amsgrad=False)
    optimizer.setup(CNNmodel)

    gpu_device = 0
    cuda.get_device(gpu_device).use()
    CNNmodel.to_gpu(gpu_device)
    xp = cuda.cupy
    X = Variable(xp.array(input_data, dtype=xp.float32))
    Y = Variable(xp.array(output_data, dtype=xp.float32))

    #X = Variable(np.array(input_data, dtype=np.float32))
    #Y = Variable(np.array(output_data, dtype=np.float32))
        

    loss_list = []
    loss_list_epoch = []
    loss_limit = STOP_ERROR
    loss_limit_flag = 0
    flag_limit = 100

    CNNmodel.cleargrads()
    #CNNmodel.zerograds()
    for i in range(0,epoch):
        #pic_group = range(0,20,pic_num_cut)
        pic_group = range(0,picture_number,pic_num_cut)
        for j in pic_group:
            jj = j+pic_num_cut
            if jj > picture_number:
                jj = picture_number
            loss = CNNmodel(X[j:jj,:,:,:],Y[j:jj,:])
            loss.backward()
            optimizer.update()
            loss = re.sub('variable','',str(loss))
            loss = loss[1:-1]
            loss = float(loss)
            loss_list.append(np.abs(loss))
        loss_list_epoch.append(np.mean(loss_list))
        loss_list.clear()

        if np.abs(loss) < loss_limit:
            loss_limit_flag = loss_limit_flag + 1
        if loss_limit_flag > flag_limit:
            file_name = 'optimum_weight_'+ str(hidden_number)
            serializers.save_npz(folder + '/' + file_name, CNNmodel)
            #print('break:',i)
            break
        if i == (epoch - 1):
            file_name = 'optimum_weight_'+ str(hiddle_number)
            serializers.save_npz(folder + '/' + file_name, CNNmodel)
            #print('break:最大学習回数に至った',epoch)
            break
    
    plt.figure(1)
    plt.plot(loss_list_epoch)
    plt.grid()
    plt.xlabel("")
    plt.ylabel("")
    plt.savefig(folder+'/'+'loss_list_epoch.pdf',bbox_inches='tight')
    
    return loss_list_epoch[-1]



def CNN_Test(input_data,
              spatial_dim,image_channel_number,image_size_x,image_size_y,
              cn1_filter_number,cn1_filter_size_x,cn1_filter_size_y,cn1_stride,cn1_padding,
              cn2_filter_number,cn2_filter_size_x,cn2_filter_size_y,cn2_stride,cn2_padding,
              cn1_pooling_size_x,cn1_pooling_size_y,
              cn2_pooling_size_x,cn2_pooling_size_y,
              hiddle_number,output_number,epoch,STOP_ERROR,dropout_pramater):
    
    """
    lx1 = math.ceil((image_size_x-cn1_filter_size_x)/cn1_stride)+1
    lx2 = math.ceil(lx1/cn1_pooling_size_x)
    lx3 = math.ceil((lx2-cn2_filter_size_x)/cn2_stride)+1
    lx4 = math.ceil(lx3/cn2_pooling_size_x)
    ly1 = math.ceil((image_size_y-cn1_filter_size_y)/cn1_stride)+1
    ly2 = math.ceil(ly1/cn1_pooling_size_y)
    ly3 = math.ceil((ly2-cn2_filter_size_y)/cn2_stride)+1
    ly4 = math.ceil(ly3/cn2_pooling_size_y)
    l1_no_1_paramater = int(cn2_filter_number*ly4*lx4)
    #print(l1_no_1_paramater)
   
    
    class MyCNN_test(Chain):
        def __init__(self):
            super(MyCNN_test,self).__init__(
                cn1 = L.ConvolutionND(spatial_dim,image_channel_number,cn1_filter_number,(cn1_filter_size_x,cn1_filter_size_y),
                                      cn1_stride,cn1_padding),
                cn2 = L.ConvolutionND(spatial_dim,cn1_filter_number,cn2_filter_number,(cn2_filter_size_x,cn2_filter_size_y),
                                      cn2_stride,cn2_padding),
                l1 = L.Linear(l1_no_1_paramater,hiddle_number),
                l2 = L.Linear(hiddle_number,output_number),
            )
        def fwd(self,x):
            h1 = F.max_pooling_nd(F.relu(self.cn1(x)),(cn1_pooling_size_x,cn1_pooling_size_y))
            h2 = F.max_pooling_nd(F.relu(self.cn2(h1)),(cn2_pooling_size_x,cn2_pooling_size_y))
            h3 = F.dropout(F.relu(self.l1(h2)),dropout_pramater)
            out_layer = self.l2(h3)
            return out_layer
     """

    class MyCNN_test(Chain):
        def __init__(self):
            super(MyCNN_test,self).__init__(
                cn1 = L.ConvolutionND(spatial_dim,image_channel_number,cn1_filter_number,(cn1_filter_size_x,cn1_filter_size_y),
                                      cn1_stride,cn1_padding),
                l1 = L.Linear(liner_in_num,hiddle_number),
                l2 = L.Linear(hiddle_number,output_number),
            )
        def fwd(self,x):
            h1 = F.max_pooling_nd(F.relu(self.cn1(x)),(cn1_pooling_size_x,cn1_pooling_size_y))
            h2 = F.dropout(F.relu(self.l1(h1)),dropout_pramater)
            out_layer = self.l2(h2)
            return out_layer

    CNNtest = MyCNN_test()
    file_name = 'optimum_weight_' + str(hiddle_number)
    serializers.load_npz(folder + '/' + file_name, CNNtest)
    
    gpu_device = 0
    cuda.get_device(gpu_device).use()
    CNNtest.to_gpu(gpu_device)
    xp2 = cuda.cupy
    X_test = Variable(xp2.array(input_data, dtype=xp2.float32))
    
    return_yy = []
    y_out = np.zeros((picture_number,output_number))
    for j in range(0,picture_number):
        #X_test = Variable(np.array(input_data[j:j+1,:,:,:], dtype=np.float32))
        X_test = Variable(xp2.array(input_data[j:j+1,:,:,:], dtype=xp2.float32))
        yy = CNNtest.fwd(X_test)
        yy = re.sub('variable','',str(yy))
        yy = yy[3:-3]
        yy = yy.split()  #yy is a list
        for k in range(0,len(yy)):
            y_out[j,k] = float(yy[k])
            y_out[j,k] = y_out[j,k] * data_out_max
    #print(y_out)
    return y_out

Image_size_x = xtrain.shape[2]
Image_size_y = xtrain.shape[3]
Output_number = ytrain.shape[1]

start_time = time.time()

return_error = CNN_Train(picture_number_cut,xtrain,ytrain,picture_number,Spatial_dim,Image_channel_number,
          Image_size_x,Image_size_y,
          Cn1_filter_number,Cn1_filter_size_x,
          Cn1_filter_size_y,Cn1_stride,Cn1_padding,Cn2_filter_number,Cn2_filter_size_x,
          Cn2_filter_size_y,Cn2_stride,Cn2_padding,Cn1_pooling_size_x,Cn1_pooling_size_y,
          Cn2_pooling_size_x,Cn2_pooling_size_y,Hiddle_number,Output_number,Epoch,STOP_ERROR,Dropout_pramater)

test_output = CNN_Test(xtrain,Spatial_dim,Image_channel_number,Image_size_x,Image_size_y,
          Cn1_filter_number,Cn1_filter_size_x,
          Cn1_filter_size_y,Cn1_stride,Cn1_padding,Cn2_filter_number,Cn2_filter_size_x,
          Cn2_filter_size_y,Cn2_stride,Cn2_padding,Cn1_pooling_size_x,Cn1_pooling_size_y,
          Cn2_pooling_size_x,Cn2_pooling_size_y,Hiddle_number,Output_number,Epoch,STOP_ERROR,Dropout_pramater)

end_time = time.time()
second = end_time-start_time
minute = 0
hour   = 0
while(second >= 60):
    second = second - 60
    minute = minute + 1
while(minute >= 60):
    minute = minute - 60
    hour   = hour   + 1
print("Learning Time : ",str(hour) + ":"+str(minute) + ":" + str(second))


figsize_x = 40
figsize_y = 10

plt.figure(2)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(data_out[:,0],label='teacher')
ax.plot(test_output[:,0],label='train')
plt.xlabel("")
plt.ylabel("")
plt.legend()
plt.grid()
plt.savefig(folder+'/'+'train_data_motor_output_left.pdf',bbox_inches='tight')




