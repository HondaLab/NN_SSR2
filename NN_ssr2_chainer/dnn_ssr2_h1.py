#!/usr/bin/python3
import numpy as np
import cv2
import csv
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain
import re
import os
import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as mt # pwmでモーターを回転させるためのモジュール
import time
import pigpio
import modules.imageCut as ic
from subprocess import Popen
import modules.camera as camera
import modules.vl53_4a as lidar
tofR,tofL,tofC=lidar.start()

with open('disdata_num_weight.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader) 
    r =  result[0]
    disdata_num = int(r[0])  
    disdata_weight = int(r[1])

one_channel = 320
input_number = (one_channel*3) + (disdata_num*3)
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

prediction_data_in = np.zeros((1,one_channel*3))
prediction_data_in2 = np.zeros((1,one_channel*3))
distance_data = np.zeros((1,3))
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

key = keyin.Keyboard()
ch="c"
print("Input q to stop.")
mL=mt.Lmotor(17)
mR=mt.Rmotor(18)

#for cap in cam.capture_continuous(rawCapture, format="bgr", use_video_port="True"):
while ch!="q":
    ch = key.read()
    try:
        if ch == "q":
            break
        camera.cam.capture(camera.rawCapture, format="bgr", use_video_port=True)
        frame = camera.rawCapture.array
        distanceL=tofL.get_distance()
        if distanceL>2000:
            distanceL=2000
        distanceC=tofC.get_distance()
        if distanceC>2000:
            distanceC=2000
        distanceR=tofR.get_distance()
        if distanceR>2000:
            distanceR=2000
        cv2.imshow('frame',frame[ic.im_cut_up:ic.im_cut_below,:,:])
        cv2.waitKey(1)
        for i in range(0,one_channel):
            prediction_data_in[0,i] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,0])
            prediction_data_in[0,i+one_channel] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,1])
            prediction_data_in[0,i+one_channel+one_channel] = sum(frame[ic.im_cut_up:ic.im_cut_below,i,2])
            
            prediction_data_in[0,i] = prediction_data_in[0,i]/data_in_max[0,i]
            prediction_data_in[0,i+one_channel] = prediction_data_in[0,i+one_channel]/data_in_max[0,i+one_channel]
            prediction_data_in[0,i+one_channel+one_channel] = prediction_data_in[0,i+one_channel+one_channel]/data_in_max[0,i+one_channel+one_channel]
        distance_data[0,0] = distanceL*disdata_weight/data_in_max[0,0]
        distance_data[0,1] = distanceC*disdata_weight/data_in_max[0,0]
        distance_data[0,2] = distanceR*disdata_weight/data_in_max[0,0]

        prediction_data_in2 = prediction_data_in
        for u in range(0,disdata_num):
            prediction_data_in2 = np.hstack((prediction_data_in2,distance_data))
        
        x_in = [[]]
        for j in range(0,prediction_data_in2.shape[1]):
            x_in[0].append(float(prediction_data_in2[0][j]))
        x_in_train = Variable(np.array(x_in,dtype=np.float32))
        yy = nn_prediction.fwd(x_in_train)
        yy = re.sub('variable','',str(yy))
        yy = yy[3:-3]
        yy = yy.split()  #yy is a list
        for k in range(0,len(yy)):
            y_out[0,k] = float(yy[k]) * data_out_max[0,k]        
        left=round(y_out[0,0])*1
        right=round(y_out[0,1])*1
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
    except KeyboardInterrupt:
        mL.run(0)
        mR.run(0)
        camera.rawCapture.truncate(0)
        break

camera.rawCapture.truncate(0)         
mL.run(0)
mR.run(0)
