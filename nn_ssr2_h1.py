#!/usr/bin/python3

import cv2
import numpy as np
#from pandas_ods_reader import read_ods
import csv
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain
import re
import os
import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as mt # pwmでモーターを回転させるためのモジュール
import modules.motor1 as sv
import modules.ctrl_5a as ctrl
import time
import pigpio
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen

view_upper=160
view_lower=250

#view_upper=50
#view_lower=319

ANGL_GAIN=1.2

one_channel = 320
input_number = one_channel*3
hidden_number = 1100
output_number = 2

with open('/tmp/data_in_max.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader)
    d_in_max = result[0]   #is list
data_in_max = np.zeros((1,len(d_in_max)))
for i in range(0,len(d_in_max)):
    data_in_max[0,i] = d_in_max[i]
    
with open('/tmp/data_out_max.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader)
    d_out_max = result[0]   #is list
data_out_max = np.zeros((1,len(d_out_max)))
for i in range(0,len(d_out_max)):
    data_out_max[0,i] = d_out_max[i]
    
#print(data_in_max)
#print(data_out_max)

RES_X=int( 320 )
RES_Y=int( 320 )
cam = PiCamera()
cam.framerate = 30
cam.awb_mode='auto'
cam.iso=400
cam.shutter_speed=1000000
cam.exposure_mode = 'auto' # off, auto, fixedfps
time.sleep(3)
g = cam.awb_gains
cam.awb_mode = 'off'
cam.awb_gains = g
cam.resolution = (RES_X, RES_Y)
cam.rotation=0
cam.meter_mode = 'average' # average, spot, backlit, matrix
cam.exposure_compensation = 0
rawCapture = PiRGBArray(cam, size=(RES_X, RES_Y))

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
file_name = '/tmp/optimum_weight_' + str(HIDDEN_UNIT)
serializers.load_npz(file_name, nn_prediction)


y_out = np.zeros((1,OUTPUT_UNIT))

key = keyin.Keyboard()
ch="c"
print("Input q to stop.")

ssr3=ctrl.Robot()

    
#for cap in cam.capture_continuous(rawCapture, format="bgr", use_video_port="True"):
while ch!="q":
    ch = key.read()
    try:
        if ch == "q":
            break
        cam.capture(rawCapture, format="bgr", use_video_port=True)
        frame = rawCapture.array
        cv2.imshow('frame',frame[view_upper:view_lower,:,:])
        cv2.waitKey(1)

        #frame = cap.array
        for i in range(0,one_channel):
            prediction_data_in[0,i] = sum(frame[view_upper:view_lower,i,0])
            prediction_data_in[0,i+one_channel] = sum(frame[view_upper:view_lower,i,1])
            prediction_data_in[0,i+one_channel+one_channel] = sum(frame[view_upper:view_lower,i,2])
            
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
        left=round(y_out[0,0])*1
        right=round(y_out[0,1])*1
        print("\r left : %5d right : %5d" % (left,right),end = '')

        if left >= 100:
            left = 99
        if left <= -100:
            left = -99
        if right >= 100:
            right = 99
        if right <= -100:
            right = -99

        ssr3.Run(left,right)
        rawCapture.truncate(0) 
    except KeyboardInterrupt:
        ssr3.stop()
        rawCapture.truncate(0)
        break

rawCapture.truncate(0)         
ssr3.stop()

