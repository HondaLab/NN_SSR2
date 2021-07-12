#!/usr/bin/python3

# ssr2_rc2a.py
# CC BY-SA Yasushi Honda 2020 2/25 

# How to execute
# sudo pigpiod
# pyhton3 hjkl1.py 

import keyin # キーボード入力を監視するモジュール
import motor5a # pwmでモーターを回転させるためのモジュール
import modules.vl53_4a as lidar
import time
import pigpio
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
import numpy as np
#import sock4robot_7a as sk

tofR,tofL,tofC=lidar.start()

import socket
import li_socket as sk
import time
#LI44 = '172.16.7.44'
zelkova58 = '172.16.7.58'
sensor_port = 50005

RES_X=int( 320 )
RES_Y=int( 320 )
cam = PiCamera()
cam.framerate = 30
cam.awb_mode='auto'
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
      
    for i in range(0,RES_X):
       picture_data.append(sum(frame[167:236,i,0]))
    for i in range(0,RES_X):
       picture_data.append(sum(frame[167:236,i,1]))
    for i in range(0,RES_X):
       picture_data.append(sum(frame[167:236,i,2]))
         
    distanceL=tofL.get_distance()
    if distanceL>2000:
        distanceL=2000
    distanceC=tofC.get_distance()
    if distanceC>2000:
        distanceC=2000
    distanceR=tofR.get_distance()
    if distanceR>2000:
        distanceR=2000
        
    picture_data.append(distanceL)
    picture_data.append(distanceC)
    picture_data.append(distanceR)
    #print(distanceL,distanceC,distanceR)
         
    picture_data.append(l)
    picture_data.append(r)
    udp.send(picture_data)
    picture_data.clear()
    rawCapture.truncate(0)

if __name__=="__main__":
   
   udp = sk.UDP_Send(zelkova58,sk.sensor_port)
   
   STEP=10
   HANDLE_STEP=14
   
   right_flag = 0
   left_flag = 0

   mL=motor5a.Lmotor(17)
   mR=motor5a.Rmotor(18)
   
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
            send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "z" :
            left-= STEP
            right-= STEP
            send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "j" :
            right = right + HANDLE_STEP
            left = left - HANDLE_STEP
            right_flag = right_flag + HANDLE_STEP
            left_flag = left_flag - HANDLE_STEP
            send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "k" :
            right = right - right_flag
            left = left - left_flag
            right_flag = 0
            left_flag = 0
            send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)

         if ch == "l" :
            right = right - HANDLE_STEP
            left = left + HANDLE_STEP
            right_flag = right_flag - HANDLE_STEP
            left_flag = left_flag + HANDLE_STEP
            send_data(left,right)
            in_data_posi = in_data_posi + 1
            Run(mL,mR,left,right)
            
         if ch == "p":
            cam.capture(rawCapture, format="bgr", use_video_port=True)
            frame = rawCapture.array
            print(frame[20,120,:])
            rawCapture.truncate(0)
            
      except KeyboardInterrupt:
         mL.run(0)
         mR.run(0)
         break

   print("\nTidying up")
   mL.run(0)
   mR.run(0)
   
