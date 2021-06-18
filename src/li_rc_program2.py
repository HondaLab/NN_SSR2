#!/usr/bin/python3

# ssr2_rc2a.py
# CC BY-SA Yasushi Honda 2020 2/25 

# How to execute
# sudo pigpiod
# pyhton3 hjkl1.py 

import keyin # キーボード入力を監視するモジュール
import motor1 # pwmでモーターを回転させるためのモジュール
#import modules.vl53_4a as lidar
import time
import pigpio
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
import numpy as np
#import sock4robot_7a as sk

# Resolution of camera ex. 640x480, 320x240
RES_X=int( 320 )
RES_Y=int( 320 )

# initialize the camera and grab a reference to the raw camera capture
cam = PiCamera()
cam.framerate = 30


#cam.brightness = 50
#cam.saturation = 50

cam.awb_mode='auto'
#   #Auto White Balance :list_awb = ['off', 'auto', 'sunlight', 'cloudy', 'shade']
cam.iso=800
cam.shutter_speed=1000000
cam.exposure_mode = 'off' # off, auto, fixedfps
time.sleep(3)
g = cam.awb_gains
cam.awb_mode = 'off'
cam.awb_gains = g

cam.resolution = (RES_X, RES_Y)
cam.rotation=0
cam.meter_mode = 'average' # average, spot, backlit, matrix
cam.exposure_compensation = 0

#udp = sk.UDP_Send(sk.ROBOT_ADDR,sk.PICAM_PORT)
#udp2mpl53 = sk.UDP_SEND(sk.MLTPICAM_BASE_ADDR,sk.PICAM22MPL53_PORT)

rawCapture = PiRGBArray(cam, size=(RES_X, RES_Y))


class input_data:
   def __init__(self,X,Y):
      self.r = np.zeros((X,Y))
      self.g = np.zeros((X,Y))
      self.b = np.zeros((X,Y))
      
data_num = 400
in_data = [input_data(RES_X,RES_Y) for i in range(data_num)]
in_data_posi = 0

f1 = open("opencv_data_in1","w")
f1.write("one")
f1.write('\t')
f1.write("two")
f1.write('\t') 
f1.write("three")
f1.write('\n') 

f2 = open("opencv_data_in2","w")
f2.write("one")
f2.write('\t')
f2.write("two")
f2.write('\t') 
f2.write("three")
f2.write('\n') 

f3 = open("opencv_data_in3","w")
f3.write("one")
f3.write('\t')
f3.write("two")
f3.write('\t') 
f3.write("three")
f3.write('\n') 


f4 = open("opencv_data_out","w")
f4.write("lm")
f4.write('\t')
f4.write("rm")
f4.write('\n')


def Run(mL,mR,left,right):
   if left<-100: left = -100
   if left>100: left = 100
   mL.run(left)
   if right<-100: right = -100
   if right>100: right = 100
   mR.run(right)
   
def write_data(l,r,n):
   if n < data_num:
      cam.capture(rawCapture, format="bgr", use_video_port=True)
      frame = rawCapture.array
     
      in_data[in_data_posi].r = frame[:,:,0]
      in_data[in_data_posi].g = frame[:,:,1]
      in_data[in_data_posi].b = frame[:,:,2]
   
      left_motor = str(l)
      f4.write(left_motor)
      f4.write('\t')
      right_motor = str(r)
      f4.write(right_motor)
      f4.write('\n')
      rawCapture.truncate(0)
   else:
      print('The data space is full')

if __name__=="__main__":
   STEP=2
   HANDLE_STEP=3
   
   right_flag = 0
   left_flag = 0

   mL=motor1.Lmotor(17)
   mR=motor1.Rmotor(18)
   
   key = keyin.Keyboard()
   ch="c"
   print("Input q to stop.")
   left=0
   right=0
   while ch!="q":
    
      ch = key.read()

      print("\r %4d %4d" % (left,right),end='')

      try:
         if ch == "a" :
            left+= STEP
            right+= STEP
            write_data(left,right,in_data_posi)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "z" :
            left-= STEP
            right-= STEP
            write_data(left,right,in_data_posi)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)
         if ch == "j" :
            right = right + HANDLE_STEP
            left = left - HANDLE_STEP
            right_flag = right_flag + HANDLE_STEP
            left_flag = left_flag - HANDLE_STEP
            write_data(left,right,in_data_posi)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "k" :
            right = right - right_flag
            left = left - left_flag
            right_flag = 0
            left_flag = 0
            write_data(left,right,in_data_posi)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "l" :
            right = right - HANDLE_STEP
            left = left + HANDLE_STEP
            right_flag = right_flag - HANDLE_STEP
            left_flag = left_flag + HANDLE_STEP
            write_data(left,right,in_data_posi)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)
            
         #if ch == "x":
            #write_data(left,right,in_data_posi)
            #in_data_posi = in_data_posi + 1
            
         #if ch == "p":
         #   cam.capture(rawCapture, format="bgr", use_video_port=True)
         #   frame = rawCapture.array
         #   print(frame[20,120,:])
         #   rawCapture.truncate(0)
      except KeyboardInterrupt:
         mL.run(0)
         mR.run(0)
         break

   print("\nTidying up")
   mL.run(0)
   mR.run(0)
   print('printing data, It will cost a few minutes,Please wait a moment')
   for k in range(0,data_num):
      for i in range(0,RES_X):
         for j in range(0,RES_Y):
            f1.write(str(in_data[k].r[i,j]))
            f1.write('\t')
            f2.write(str(in_data[k].g[i,j]))
            f2.write('\t')
            f3.write(str(in_data[k].b[i,j]))
            f3.write('\t')
         f1.write('\n')
         f2.write('\n')
         f3.write('\n')
         
      f1.write('MMM')
      f1.write('\n')
      f2.write('MMM')
      f2.write('\n')
      f3.write('MMM')
      f3.write('\n')
      
   print('printing data is finished')
