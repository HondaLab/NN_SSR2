#!/usr/bin/python3
import numpy as np
import math
import cv2
import csv
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain
import re
import os
#import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as mt # pwmでモーターを回転させるためのモジュール
import time
import pigpio
import modules.imageCut as ic
from subprocess import Popen
import modules.camera as camera
import threading
#from multiprocessing import Process
import modules.vl53_4a as lidar

class lastData:
    def __init__(self,lnl,lnr,lml,lmr):
        self.last_nnL = lnl
        self.last_nnR = lnr
        self.last_ML = lml
        self.last_MR = lmr
LD = lastData(20,20,30,30)
class Mout:
    def __init__(self,a,b):
        self.powerL = a
        self.powerR = b
        self.proces = 1
MOUT = Mout(0,0)
tofR,tofL,tofC=lidar.start()
def tanh1(x):
    alpha=30.0
    alpha2=30.0
    beta=0.004
    beta2=10.00
    b=200
    c=0.0
    f=alpha*math.tanh(beta*(x-b)) + alpha2*math.tanh(beta2*(x-b))+c
    return f
def tanhMotor():
    gamma=0.33
    while MOUT.proces:
        distanceL=tofL.get_distance()
        time.sleep(0.03)
        if distanceL>2000:
            distanceL=2000
        distanceC=tofC.get_distance()
        time.sleep(0.03)
        if distanceC>2000:
            distanceC=2000
        distanceR=tofR.get_distance()
        time.sleep(0.03)
        if distanceR>2000:
            distanceR=2000
        #print(distanceL,"            ",distanceC,"            ",distanceR)
        if distanceL>0 and distanceC>0:
            areaL=math.exp(gamma*math.log(distanceC))*math.exp((1-gamma)*math.log(distanceL))
        if distanceR>0 and distanceC>0:
            areaR=math.exp(gamma*math.log(distanceC))*math.exp((1-gamma)*math.log(distanceR))
        MOUT.powerL=tanh1(areaR)
        MOUT.powerR=tanh1(areaL)
        time.sleep(0.03)
p = threading.Thread(target=tanhMotor)
p.start()

def Model_Accommodate(nnL,nnR,ML,MR):
    sw = abs(LD.last_nnL-nnL)+abs(LD.last_ML-ML)
    if sw <= 0:
        outL = nnL
        outR = nnR
    else:
        outL = ((nnL*abs(LD.last_nnL-nnL))+(ML*abs(LD.last_ML-ML)))/sw
        outR = ((nnR*abs(LD.last_nnR-nnR))+(MR*abs(LD.last_MR-MR)))/sw
    LD.last_nnL = nnL
    LD.last_nnR = nnR
    LD.last_ML = ML
    LD.last_MR = MR
    return np.floor(outL),np.floor(outR)
    #return ML,MR
    #return nnL,nnR

one_channel = 320
input_number = one_channel*3
hidden_number = 1000
output_number = 2

with open('Input_data_max.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader)
    d_in_max = result[0]   #is list
data_in_max = np.zeros((1,len(d_in_max)))
for i in range(0,len(d_in_max)):
    data_in_max[0,i] = d_in_max[i]
    
with open('Output_data_max.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader)
    d_out_max = result[0]   #is list
data_out_max = np.zeros((1,len(d_out_max)))
for i in range(0,len(d_out_max)):
    data_out_max[0,i] = d_out_max[i]
    
#print(data_in_max)
#print(data_out_max)

prediction_data_in = np.zeros((1,input_number))
INPUT_UNIT = input_number  #入力層のユニット
HIDDEN_UNIT = hidden_number #中間層のユニット
OUTPUT_UNIT = output_number #出力層のユニット
        
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

y_out = np.zeros((1,OUTPUT_UNIT))

#key = keyin.Keyboard()
ch="c"
print("Input q to stop.")
mL=mt.Lmotor(17)
mR=mt.Rmotor(18)

#for cap in cam.capture_continuous(rawCapture, format="bgr", use_video_port="True"):
TIME = 10
start = time.time()
while ch!="q":
    #ch = key.read()
    try:
        #if ch == "q":
            #break
        camera.cam.capture(camera.rawCapture, format="bgr", use_video_port=True)
        frame = camera.rawCapture.array
        #cv2.imshow('frame',frame[ic.im_cut_up:ic.im_cut_below,:,:])
        #cv2.waitKey(1)
        for i in range(0,one_channel):
            prediction_data_in[0,i] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,0])
            prediction_data_in[0,i+one_channel] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,1])
            prediction_data_in[0,i+one_channel+one_channel] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,2])
            
            prediction_data_in[0,i] = prediction_data_in[0,i]/data_in_max[0,i]
            prediction_data_in[0,i+one_channel] = prediction_data_in[0,i+one_channel]/data_in_max[0,i+one_channel]
            prediction_data_in[0,i+one_channel+one_channel] = prediction_data_in[0,i+one_channel+one_channel]/data_in_max[0,i+one_channel+one_channel]
        x_in = [[]]
        for j in range(0,prediction_data_in.shape[1]):
            x_in[0].append(float(prediction_data_in[0][j]))
        x_in_train = Variable(np.array(x_in,dtype=np.float32))
        yy = nn_prediction.fwd(x_in_train)
        yy = re.sub('variable','',str(yy))
        yy = yy[3:-3]
        yy = yy.split()  #yy is a list
        for k in range(0,len(yy)):
            y_out[0,k] = float(yy[k]) * data_out_max[0,k]        
        nnleft=round(y_out[0,0])*1
        nnright=round(y_out[0,1])*1
        left,right = Model_Accommodate(nnleft,nnright,MOUT.powerL,MOUT.powerR)
        print('\r',end = '')
        print("left : ",left,"      ","right : ",right,end = '')
        if left >= 100:
            left = 99
        if left <= -100:
            left = -99
        if right >= 100:
            right = 99
        if right <= -100:
            right = -99
        mL.run(left)
        mR.run(right)
        camera.rawCapture.truncate(0) 
        end = time.time()
        if end-start > TIME:
            print("\n")
            print("Time : ",np.floor(end-start))
            break
    except KeyboardInterrupt:
        mL.run(0)
        mR.run(0)
        camera.rawCapture.truncate(0)
        break

camera.rawCapture.truncate(0)  
MOUT.proces = 0
mL.run(0)
mR.run(0)

