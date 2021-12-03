#!/usr/bin/python3
import numpy as np
import cupy as cp
import matplotlib.pyplot as plt
import time
import pandas as pd
import os
import csv
import random
start_time = time.time()
#############The parametar of CNN############
img_w = 320
BGR = 3
filter_num_cov1 = 25
flt_h_cov1 = 8
flt_w_cov1 = 8
stride_cov1 =8
pad_cov1 = 0
pool1 = 2
pad_pol1 = 0
num_M1 = 1600
output_number = 2
wb_width_cov1 = 0.01
wb_width_M1 = 0.01
eta = 0.01
############The parametar of ABC##############
#STOP_ERROR = 0.0001
STOP_LIMIT = 100
stop_count = 0
self_or_global_search = 0.6
self_elpha = 0.6
global_elpha = 0.2
maxCycle = 4000
employed_bee_num = 8
follower_bee_num = 17
#scouter_bee_num = 10
search_limit = 50
###################################################
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
img_h = limit_below-limit_top ######
print("Image cut size : ",img_cut_size)

#file_name = os.path.basename('_chainer_neural_network_hidden_change')
#folder = 'output' + file_name
folder = 'output_ABCCNN'
if not os.path.exists(folder):
    os.mkdir(folder)

path2 = "CNN_motor_out.csv"
data_out = pd.read_csv(path2,header=None)
data_out = data_out.values
#print(data_out.shape)
ytrain = cp.ones((data_out.shape[0],data_out.shape[1]))

data_out_max = data_out.max()
data_out_max_list = []
data_out_max_list.append(data_out_max)
ytrain = cp.asarray(data_out)/data_out_max
        
f2 = open(folder+'/'+'data_out_max.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2)
csv_writer2.writerow(data_out_max_list)      
f2.close()
picture_number = ytrain.shape[0]

xtrain_0 = np.zeros((picture_number,BGR,limit_below-limit_top,img_w))
xtrain = cp.ones((picture_number,BGR,limit_below-limit_top,img_w))
flag = 0
pic_num = 0
for u in range(0,data1.shape[0]):
    if data1[u,0] != "M":
        a = data1[u,0]
        b = a.split("\t")
        for v in range(0,320):
            xtrain_0[pic_num,0,flag,v] = b[v]
        a = data2[u,0]
        b = a.split("\t")
        for v in range(0,320):
            xtrain_0[pic_num,1,flag,v] = b[v]
        a = data3[u,0]
        b = a.split("\t")
        for v in range(0,320):
            xtrain_0[pic_num,2,flag,v] = b[v]    
        flag = flag + 1
    else:
        flag = 0
        pic_num = pic_num + 1
data_in_max = xtrain_0.max()
data_in_max_list = []
data_in_max_list.append(data_in_max)
xtrain = cp.asarray(xtrain_0)/data_in_max
f = open(folder+'/'+'data_in_max.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)       
csv_writer.writerow(data_in_max_list)        
f.close()
del data1,data2,data3,xtrain_0
print("picture number : ",pic_num)
#print(type(ytrain),type(xtrain))
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
########################Reading data finished##################################################################

class BEE:
    def __init__(self,x_ch_cov1,x_h_cov1,x_w_cov1,n_flt_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,
                      pool1,pad_pol1,
                      num_M1):

        self.w_cov1 = wb_width_cov1 * cp.random.randn(n_flt_cov1,x_ch_cov1,flt_h_cov1,flt_w_cov1)#最適化する
        self.b_cov1 = wb_width_cov1 * cp.random.randn(1,n_flt_cov1)#最適化する
        self.y_ch_cov1 = n_flt_cov1
        self.y_h_cov1 = (x_h_cov1 - flt_h_cov1 + 2*pad_cov1) // stride_cov1 + 1
        self.y_w_cov1 = (x_w_cov1 - flt_w_cov1 + 2*pad_cov1) // stride_cov1 + 1

        self.y_ch_pol1 = self.y_ch_cov1
        self.y_h_pol1 = self.y_h_cov1 // pool1 if self.y_h_cov1 % pool1 == 0 else self.y_h_cov1 // pool1 + 1
        self.y_w_pol1 = self.y_w_cov1 // pool1 if self.y_w_cov1 % pool1 == 0 else self.y_w_cov1 // pool1 + 1

        self.num_in_M1 = self.y_ch_pol1 * self.y_h_pol1 * self.y_w_pol1
        self.w_M1 = wb_width_M1 * cp.random.randn(self.num_in_M1,num_M1)#最適化する
        self.b_M1 = wb_width_M1 * cp.random.randn(num_M1)#最適化する

        self.w_Out = wb_width_M1 * cp.random.randn(num_M1,output_number)#最適化する
        self.b_Out = wb_width_M1 * cp.random.randn(output_number)#最適化する

def im2col(images,flt_h,flt_w,out_h,out_w,stride,pad):
    n_bt,n_ch,img_h,img_w = images.shape
    img_pad = cp.pad(images,[(0,0),(0,0),(pad,pad),(pad,pad)],"constant")
    cols = cp.ones((n_bt,n_ch,flt_h,flt_w,out_h,out_w))
    for h in range(flt_h):
        h_lim = h + stride*out_h
        for w in range(flt_w):
            w_lim = w + stride*out_w
            cols[:,:,h,w,:,:] = img_pad[:,:,h:h_lim:stride,w:w_lim:stride]
    cols = cols.transpose(1,2,3,0,4,5).reshape(n_ch*flt_h*flt_w,n_bt*out_h*out_w)
    return cols
def col2im(cols,img_shape,flt_h,flt_w,out_h,out_w,stride,pad):
    n_bt,n_ch,img_h,img_w = img_shape
    cols = cols.reshape(n_ch,flt_h,flt_w,n_bt,out_h,out_w).transpose(3,0,1,2,4,5)
    images = cp.ones((n_bt,n_ch,img_h+2*pad+stride-1,img_w+2*pad+stride-1))
    for h in range(flt_h):
        h_lim = h + stride*out_h
        for w in range(flt_w):
            w_lim = w + stride*out_w
            images[:,:,h:h_lim:stride,w:w_lim:stride] += cols[:,:,h,w,:,:]
    return images[:,:,pad:img_h+pad,pad:img_w+pad]

def forward(Bee):
#########Convolutional layer#####################
    n_bt = xtrain.shape[0]
    cols_cov1 = im2col(xtrain,flt_h_cov1,flt_w_cov1,Bee.y_h_cov1,Bee.y_w_cov1,stride_cov1,pad_cov1)
    w_col_cov1 = Bee.w_cov1.reshape(filter_num_cov1,BGR*flt_h_cov1*flt_w_cov1)
    u_cov1 = cp.dot(w_col_cov1,cols_cov1).T + Bee.b_cov1
    u_cov1 = u_cov1.reshape(n_bt,Bee.y_h_cov1,Bee.y_w_cov1,Bee.y_ch_cov1).transpose(0,3,1,2) #数字の意味不明
    y_cov1 = cp.where(u_cov1 <= 0,0,u_cov1)
    #print(y_cov1.shape)
###############Pooling layer#######################
    n_bt_pol1 = y_cov1.shape[0]
    cols_pol1 = im2col(y_cov1,pool1,pool1,Bee.y_h_pol1,Bee.y_w_pol1,pool1,pad_pol1)
    cols_pol1 = cols_pol1.T.reshape(n_bt*Bee.y_h_pol1*Bee.y_w_pol1*Bee.y_ch_pol1,pool1*pool1)
    y_pol1 = cp.max(cols_pol1,axis = 1)
    y_pol1 = y_pol1.reshape(n_bt_pol1,Bee.y_h_pol1,Bee.y_w_pol1,Bee.y_ch_pol1).transpose(0,3,1,2)
    max_index_pol1 = cp.argmax(cols_pol1,axis=1)
#########Convolutional layer 2#####################
################Fully connected layer##############
    input_M1 = y_pol1.reshape(n_bt_pol1,-1)
    u_M1 = cp.dot(input_M1,Bee.w_M1) + Bee.b_M1
    y_M1 = cp.where(u_M1 <= 0,0,u_M1)
##################Output layer#####################
    y_Out = cp.dot(y_M1,Bee.w_Out) + Bee.b_Out
    #squared_error = sum(sum((y_Out-ytrain)*(y_Out-ytrain)))
    return y_Out

def forward_loss(b):
    y = forward(b)
    squared_error = sum(sum((y-ytrain)*(y-ytrain)))
    return squared_error
"""
def Squared_Error(x,y):
    #print(sum(sum((x-y)*(x-y))))
    squared_error = sum(sum((x-y)*(x-y)))
    return squared_error
"""
def Bee_Search(bee1,bee2,coefficient):
    bee1.w_cov1 = bee1.w_cov1 + ((random.random()-0.5)*coefficient*(bee2.w_cov1-bee1.w_cov1))
    bee1.b_cov1 = bee1.b_cov1 + ((random.random()-0.5)*coefficient*(bee2.b_cov1-bee1.b_cov1))
    bee1.w_M1 = bee1.w_M1 + ((random.random()-0.5)*coefficient*(bee2.w_M1-bee1.w_M1))
    bee1.b_M1 = bee1.b_M1 + ((random.random()-0.5)*coefficient*(bee2.b_M1-bee1.b_M1))
    bee1.w_Out = bee1.w_Out + ((random.random()-0.5)*coefficient*(bee2.w_Out-bee1.w_Out))
    bee1.b_Out = bee1.b_Out + ((random.random()-0.5)*coefficient*(bee2.b_Out-bee1.b_Out))
    return bee1
########################## ABC ##################################
GlobalMin = 9999999999
GlobalMinList = []
fitness = cp.ones((1,employed_bee_num))
life_count = cp.ones((1,employed_bee_num))  # bee will be killed if it over than search_limit
probability = cp.ones((1,employed_bee_num))
GlobalBestBee = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
TemporaryBee = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
employed_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(employed_bee_num)]
follower_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(follower_bee_num)]
#scouter_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(scouter_bee_num)]

for i in range(0,employed_bee_num):
    fitness[0,i] = forward_loss(employed_bee[i])
    if fitness[0,i] < GlobalMin:
        GlobalMin = fitness[0,i]
        GlobalBestBee = employed_bee[i]

for ABC_cyc in range(maxCycle):
    """
    print("1 : ",fitness)
    print("2 : ",GlobalMin)
    print("3 : ",GlobalMinList)
    print("###############################3")
    """
    GlobalMinList.append(int(GlobalMin))
    ########### employed bee ######################
    for eb in range(0,employed_bee_num):
        if random.random() < self_or_global_search:
            critical_domain_num = eb
            while critical_domain_num == eb:
                critical_domain_num = random.randint(0,employed_bee_num-1)
            TemporaryBee = Bee_Search(employed_bee[eb],employed_bee[critical_domain_num],self_elpha)
            TemporaryFitness = forward_loss(TemporaryBee)
            if TemporaryFitness < fitness[0,eb]:
                life_count[0,eb] = 0
                fitness[0,eb] = TemporaryFitness
                employed_bee[eb] = TemporaryBee
                if fitness[0,eb] < GlobalMin:
                    GlobalMin = fitness[0,eb]
                    GlobalBestBee = employed_bee[eb]
                    stop_count = 0
                else:
                    stop_count = stop_count + 1
            else:
                life_count[0,eb] = life_count[0,eb] + 1
                
        else:
            TemporaryBee = Bee_Search(employed_bee[eb],GlobalBestBee,global_elpha)
            TemporaryFitness = forward_loss(TemporaryBee)
            if TemporaryFitness < fitness[0,eb]:
                life_count[0,eb] = 0
                fitness[0,eb] = TemporaryFitness
                employed_bee[eb] = TemporaryBee
                if fitness[0,eb] < GlobalMin:
                    GlobalMin = fitness[0,eb]
                    GlobalBestBee = employed_bee[eb]
                    stop_count = 0
                else:
                    stop_count = stop_count + 1
            else:
                life_count[0,eb] = life_count[0,eb] + 1
     ################# select probability ################
    maxFitness = max(fitness[0,:])
    for f in range(employed_bee_num):
        probability[0,f] = 0.9*(fitness[0,f]/maxFitness)+0.1
    ################ follower bee #######################
    p = -1 #employed bee loop
    t = -1 #follower bee loop
    while t <= follower_bee_num:
        p = p + 1
        if p == employed_bee_num:
            p = 0
        if random.random() < probability[0,p]:
            t = t + 1
            if random.random() < self_or_global_search:
                critical_domain_num = p
                while critical_domain_num == p:
                    critical_domain_num = random.randint(0,employed_bee_num-1)
                TemporaryBee = Bee_Search(employed_bee[p],employed_bee[critical_domain_num],self_elpha)
                TemporaryFitness = forward_loss(TemporaryBee)
                if TemporaryFitness < fitness[0,p]:
                    life_count[0,p] = 0
                    fitness[0,p] = TemporaryFitness
                    employed_bee[p] = TemporaryBee
                    if fitness[0,eb] < GlobalMin:
                        GlobalMin = fitness[0,eb]
                        GlobalBestBee = employed_bee[eb]
                        stop_count = 0
                    else:
                        stop_count = stop_count + 1
                else:
                    life_count[0,p] = life_count[0,p] + 1
                  
            else:
                TemporaryBee = Bee_Search(employed_bee[p],GlobalBestBee,global_elpha)
                TemporaryFitness = forward_loss(TemporaryBee)
                if TemporaryFitness < fitness[0,p]:
                    life_count[0,p] = 0
                    fitness[0,p] = TemporaryFitness
                    employed_bee[p] = TemporaryBee
                    if fitness[0,eb] < GlobalMin:
                        GlobalMin = fitness[0,eb]
                        GlobalBestBee = employed_bee[eb]
                        stop_count = 0
                    else:
                        stop_count = stop_count + 1
                else:
                    life_count[0,p] = life_count[0,p] + 1
        else:
            life_count[0,p] = life_count[0,p] + 2

    if stop_count>STOP_LIMIT:
        break
    ############# scouter bee ######################
    for sc in range(0,employed_bee_num):
        if life_count[0,sc] > search_limit:
            employed_bee[sc] = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
            life_count[0,sc] = 0    

trained_out = forward(GlobalBestBee)*data_out_max

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
print("Training Time : ",str(hour) + ":"+str(minute) + ":" + str(second))

#print(GlobalMinList)

figsize_x = 20
figsize_y = 10
plt.figure(1)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(GlobalMinList)
plt.xlabel("")
plt.ylabel("")
plt.grid()
plt.savefig(folder+'/'+'error.pdf',bbox_inches='tight')

figsize_x = 40
figsize_y = 10
plt.figure(2)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(data_out[:,0],label='teacher')
ax.plot(cp.asnumpy(trained_out[:,0]),label='train')
plt.xlabel("")
plt.ylabel("")
plt.legend()
plt.grid()
plt.savefig(folder+'/'+'left_motor_output.pdf',bbox_inches='tight')

plt.figure(3)
fig = plt.figure(figsize=(figsize_x,figsize_y))
ax = fig.add_subplot(111)
ax.plot(data_out[:,1],label='teacher')
ax.plot(cp.asnumpy(trained_out[:,1]),label='train')
plt.xlabel("")
plt.ylabel("")
plt.legend()
plt.grid()
plt.savefig(folder+'/'+'right_motor_output.pdf',bbox_inches='tight')


