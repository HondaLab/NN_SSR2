import numpy as np
import cv2
import csv
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable, optimizers, serializers, Chain
import re
import os
import keyin # キーボード入力を監視するモジュール
import motor5a as mt # pwmでモーターを回転させるためのモジュール
import time
import pigpio
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen


wise_direction = 'a'
if str(wise_direction) == 'c':
    folder = 'clockwise/hidden1'
if str(wise_direction) == 'a':
    folder = 'anticlockwise/hidden1'


with open(folder +'/'+'data_in_max.csv','r') as f:
    reader = csv.reader(f)
    result = list(reader)
    d_in_max = result[0]   #is list
data_in_max = np.zeros((1,len(d_in_max)))
for i in range(0,len(d_in_max)):
    data_in_max[0,i] = d_in_max[i]
    
with open(folder +'/'+'data_out_max.csv','r') as f:
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
blue = np.zeros((1,RES_Y))
green = np.zeros((1,RES_Y))
red = np.zeros((1,RES_Y))

input_number = RES_Y*3
output_number = 2
im_cut_up = 172
im_cut_below = 236

cam = PiCamera()
cam.framerate = 5
cam.awb_mode='auto'
cam.iso=800
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

prediction_data_in_0 = np.zeros((1,RES_Y*2))
prediction_data_in = np.zeros((1,input_number))
INPUT_UNIT = input_number  #入力層のユニット
HIDDEN_UNIT_1 = 1000 #中間層のユニット
HIDDEN_UNIT_2 = 1000 #中間層のユニット
OUTPUT_UNIT = output_number #出力層のユニット
        
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
file_name = 'optimum_weight_' + str(HIDDEN_UNIT_1) + '_' + str(HIDDEN_UNIT_2)
serializers.load_npz(folder + '/' + file_name, nn_prediction)


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
        cam.capture(rawCapture, format="bgr", use_video_port=True)
        frame = rawCapture.array
        cv2.imshow('frame',frame[im_cut_up:im_cut_below,:,:])
        cv2.waitKey(1)
        for i in range(0,RES_Y):
            blue[0,i] = sum(frame[im_cut_up:im_cut_below,i,0])/data_in_max[0,i]
            green[0,i] = sum(frame[im_cut_up:im_cut_below,i,1])/data_in_max[0,i+320]
            red[0,i] = sum(frame[im_cut_up:im_cut_below,i,2])/data_in_max[0,i+640]
        prediction_data_in_0[0,:] = np.append(blue,green)
        prediction_data_in[0,:] = np.append(prediction_data_in_0,red)
        #english333print(prediction_data_in.shape)
        #prediction_data_in[0,i] = prediction_data_in[0,i]/data_in_max[0,i]
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
        left=y_out[0,0]
        right=y_out[0,1]
        print('\r',end = '')
        print("left : ",left,"       ","right : ",right,end = '')
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
        rawCapture.truncate(0) 
    except KeyboardInterrupt:
        mL.run(0)
        mR.run(0)
        rawCapture.truncate(0)
        break

rawCapture.truncate(0)       
mL.run(0)
mR.run(0)
 