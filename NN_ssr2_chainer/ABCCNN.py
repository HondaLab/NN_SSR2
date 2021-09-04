import numpy as np
import time
import pandas as pd
import os
import csv
import random
start_time = time.time()
#############The parametar of CNN############
img_w = 320
BGR = 3
filter_num_cov1 = 10
flt_h_cov1 = 8
flt_w_cov1 = 8
stride_cov1 =8
pad_cov1 = 0
pool1 = 2
pad_pol1 = 0
num_M1 = 200
output_number = 2
wb_width_cov1 = 0.1
wb_width_M1 = 0.1
eta = 0.01
############The parametar of ABC##############
#STOP_ERROR = 0.0001
STOP_LIMIT = 200
stop_count = 0
self_or_global_search = 0.6
self_elpha = 0.8
global_elpha = 0.6
maxCycle = 5
employed_bee_num = 4
follower_bee_num = 7
#scouter_bee_num = 10
search_limit = 10
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
folder = 'ABCCNNoutput'
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
xtrain = np.zeros((picture_number,BGR,limit_below-limit_top,img_w))
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

########################Reading data finished##################################################################

def im2col(images,flt_h,flt_w,out_h,out_w,stride,pad):
    n_bt,n_ch,img_h,img_w = images.shape
    img_pad = np.pad(images,[(0,0),(0,0),(pad,pad),(pad,pad)],"constant")
    cols = np.zeros((n_bt,n_ch,flt_h,flt_w,out_h,out_w))
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
    images = np.zeros((n_bt,n_ch,img_h+2*pad+stride-1,img_w+2*pad+stride-1))
    for h in range(flt_h):
        h_lim = h + stride*out_h
        for w in range(flt_w):
            w_lim = w + stride*out_w
            images[:,:,h:h_lim:stride,w:w_lim:stride] += cols[:,:,h,w,:,:]
    return images[:,:,pad:img_h+pad,pad:img_w+pad]

class BEE:
    def __init__(self,x_ch_cov1,x_h_cov1,x_w_cov1,n_flt_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,
                      pool1,pad_pol1,
                      num_M1):

        self.w_cov1 = wb_width_cov1 * np.random.randn(n_flt_cov1,x_ch_cov1,flt_h_cov1,flt_w_cov1)#最適化する
        self.b_cov1 = wb_width_cov1 * np.random.randn(1,n_flt_cov1)#最適化する
        self.y_ch_cov1 = n_flt_cov1
        self.y_h_cov1 = (x_h_cov1 - flt_h_cov1 + 2*pad_cov1) // stride_cov1 + 1
        self.y_w_cov1 = (x_w_cov1 - flt_w_cov1 + 2*pad_cov1) // stride_cov1 + 1

        self.y_ch_pol1 = self.y_ch_cov1
        self.y_h_pol1 = self.y_h_cov1 // pool1 if self.y_h_cov1 % pool1 == 0 else self.y_h_cov1 // pool1 + 1
        self.y_w_pol1 = self.y_w_cov1 // pool1 if self.y_w_cov1 % pool1 == 0 else self.y_w_cov1 // pool1 + 1

        self.num_in_M1 = self.y_ch_pol1 * self.y_h_pol1 * self.y_w_pol1
        self.w_M1 = wb_width_M1 * np.random.randn(self.num_in_M1,num_M1)#最適化する
        self.b_M1 = wb_width_M1 * np.random.randn(num_M1)#最適化する

        self.w_Out = wb_width_M1 * np.random.randn(num_M1,output_number)#最適化する
        self.b_Out = wb_width_M1 * np.random.randn(output_number)#最適化する

def forward(Bee):
#########Convolutional layer#####################
    n_bt = xtrain.shape[0]
    cols_cov1 = im2col(xtrain,flt_h_cov1,flt_w_cov1,Bee.y_h_cov1,Bee.y_w_cov1,stride_cov1,pad_cov1)
    w_col_cov1 = Bee.w_cov1.reshape(filter_num_cov1,BGR*flt_h_cov1*flt_w_cov1)
    u_cov1 = np.dot(w_col_cov1,cols_cov1).T + Bee.b_cov1
    u_cov1 = u_cov1.reshape(n_bt,Bee.y_h_cov1,Bee.y_w_cov1,Bee.y_ch_cov1).transpose(0,3,1,2) #数字の意味不明
    y_cov1 = np.where(u_cov1 <= 0,0,u_cov1)
    #print(y_cov1.shape)
###############Pooling layer#######################
    n_bt_pol1 = y_cov1.shape[0]
    cols_pol1 = im2col(y_cov1,pool1,pool1,Bee.y_h_pol1,Bee.y_w_pol1,pool1,pad_pol1)
    cols_pol1 = cols_pol1.T.reshape(n_bt*Bee.y_h_pol1*Bee.y_w_pol1*Bee.y_ch_pol1,pool1*pool1)
    y_pol1 = np.max(cols_pol1,axis = 1)
    y_pol1 = y_pol1.reshape(n_bt_pol1,Bee.y_h_pol1,Bee.y_w_pol1,Bee.y_ch_pol1).transpose(0,3,1,2)
    max_index_pol1 = np.argmax(cols_pol1,axis=1)
################Fully connected layer##############
    input_M1 = y_pol1.reshape(n_bt_pol1,-1)
    u_M1 = np.dot(input_M1,Bee.w_M1) + Bee.b_M1
    y_M1 = np.where(u_M1 <= 0,0,u_M1)
##################Output layer#####################
    y_Out = np.dot(y_M1,Bee.w_Out) + Bee.b_Out
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

##################ABC##################################################33
GlobalMin = 999999999
GlobalMinList = []
fitness = np.zeros((1,employed_bee_num))
life_count = np.zeros((1,employed_bee_num))  # bee will be killed if it over than search_limit
probability = np.zeros((1,employed_bee_num))
GlobalBestBee = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
TemporaryBee = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
employed_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(employed_bee_num)]
follower_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(follower_bee_num)]
#scouter_bee = [BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1) for i in range(scouter_bee_num)]

for i in range(0,employed_bee_num):
    fitness[0,i] = forward_loss(employed_bee[i])
    if fitness[0,i] <= GlobalMin:
        GlobalMin = fitness[0,i]
        GlobalBestBee = employed_bee[i]

for ABC_cyc in range(maxCycle):
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
                    #GlobalMinList.append(GlobalMin)
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
                    if fitness[0,p] < GlobalMin:
                        GlobalMin = fitness[0,p]
                        GlobalBestBee = employed_bee[p]
                        #GlobalMinList.append(GlobalMin)
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
                    if fitness[0,p] < GlobalMin:
                        GlobalMin = fitness[0,p]
                        GlobalBestBee = employed_bee[p]
                        #GlobalMinList.append(GlobalMin)
                        stop_count = 0
                    else:
                        stop_count = stop_count + 1
                else:
                    life_count[0,p] = life_count[0,p] + 1
        else:
            life_count[0,p] = life_count[0,p] + 2
        
    ############# scouter bee ######################
    for sc in range(0,employed_bee_num):
        if life_count[0,sc] > search_limit:
            employed_bee[sc] = BEE(BGR,img_h,img_w,filter_num_cov1,flt_h_cov1,flt_w_cov1,stride_cov1,pad_cov1,pool1,pad_pol1,num_M1)
            life_count[0,sc] = 0
    GlobalMinList.append(GlobalMin)
    if stop_count>STOP_LIMIT:
        break

print(GlobalMinList)

















