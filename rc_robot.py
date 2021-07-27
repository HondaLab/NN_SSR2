#!/usr/bin/python3

# ssr2_rc2a.py
# CC BY-SA Yasushi Honda 2020 2/25 

# How to execute
# sudo pigpiod
# pyhton3 hjkl1.py 

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as mt # pwmでモーターを回転させるためのモジュール
import modules.li_socket as sk
#import modules.vl53_4a as lidar
import time
import pigpio
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
import numpy as np


import socket
import time

view_upper=130
view_lower=270


RES_X=int( 320 )
RES_Y=int( 320 )
cam = PiCamera()
cam.framerate = 30
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

#moter_data = [0,0]
#tof_data = [0,0,0]
in_data_posi = 0
picture_data = []

def Run(mL,mR,left,right):
   if left<-100: left = -100
   if left>100: left = 100
   mL.run(left)
   if right<-100: right = -100
   if right>100: right = 100
   mR.run(right)
   
def send_data(l,r):
      cam.capture(rawCapture, format="bgr", use_video_port=True)
      frame = rawCapture.array
      
      cv2.imshow('frame',frame[view_upper:view_lower,:,:])
      cv2.waitKey(1)
      
      for i in range(0,RES_X):
         picture_data.append(sum(frame[view_upper:view_lower,i,0]))
      for i in range(0,RES_X):
         picture_data.append(sum(frame[view_upper:view_lower,i,1]))
      for i in range(0,RES_X):
         picture_data.append(sum(frame[view_upper:view_lower,i,2]))
      picture_data.append(l)
      picture_data.append(r)
      udp.send(picture_data)
      picture_data.clear()
      rawCapture.truncate(0)

if __name__=="__main__":
   
   udp = sk.UDP_Send(sk.learning_machine,sk.sensor_port)
   
   STEP=10
   HANDLE_STEP=14
   
   right_flag = 0
   left_flag = 0

   mL=mt.Lmotor(17)
   mR=mt.Rmotor(18)
   
   key = keyin.Keyboard()
   ch="c"
   print("Input q to stop.")
   now=time.time()
   start=now
   init=now
   left=0
   right=0
   while ch!="q":
    
      ch = key.read()

      print("\r %4d %4d" % (left,right),end='')

      try:

         if ch == "a" :
            left+= STEP
            right+= STEP
            #send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "z" :
            left-= STEP
            right-= STEP
            #send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "j" :
            right = right + HANDLE_STEP
            left = left - HANDLE_STEP
            right_flag = right_flag + HANDLE_STEP
            left_flag = left_flag - HANDLE_STEP
            #send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "k" :
            right = right - right_flag
            left = left - left_flag
            right_flag = 0
            left_flag = 0
            #send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "l" :
            right = right - HANDLE_STEP
            left = left + HANDLE_STEP
            right_flag = right_flag - HANDLE_STEP
            left_flag = left_flag + HANDLE_STEP
            #send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)
            
         if ch == "p":
            cam.capture(rawCapture, format="bgr", use_video_port=True)
            frame = rawCapture.array
            print(frame[20,120,:])
            rawCapture.truncate(0)

         if now-init>0.1:
            send_data(left,right)
            init=now
         
         now=time.time() 
      
      except KeyboardInterrupt:
         mL.run(0)
         mR.run(0)
         break

   print("\nTidying up")
   mL.run(0)
   mR.run(0)
   
