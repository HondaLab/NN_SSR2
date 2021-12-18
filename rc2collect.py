#!/usr/bin/python3

# you need
# sudo pigpiod

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.socket as sk
import modules.tof4_6a as tof 
import modules.camera as camera
import modules.rc3c as ctrl
import time
import pigpio
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
import numpy as np

import socket
import time


view_upper=80
view_lower=320

data = []

def Send(frame,left,right):
   '''
   If run==True, this function moves both left and right motors.
   Moreover these training data are send to the server to learn NN weights.
   '''


   for i in range(0,camera.RES_X):
      data.append(sum(frame[view_upper:view_lower,i,0]))
   for i in range(0,camera.RES_X):
      data.append(sum(frame[view_upper:view_lower,i,1]))
   for i in range(0,camera.RES_X):
      data.append(sum(frame[view_upper:view_lower,i,2]))

   distanceL=tofL.get_distance()
   if distanceL>2000:
      distanceL=2000
   distanceC=tofC.get_distance()
   if distanceC>2000:
      distanceC=2000
   distanceR=tofR.get_distance()
   if distanceR>2000:
      distanceR=2000
   #print("\r %4d %4d" % (distanceL,distanceC,distanceR),end='')
   data.append(distanceL)
   data.append(distanceC)
   data.append(distanceR)

   if left<-100: left = -99
   if left>100: left = 99
   if right<-100: right = -99
   if right>100: right = 99
   data.append(left)
   data.append(right)

   udp.send(data)
   data.clear()


if __name__=="__main__":
   
   tofR,tofL,tofC,tofM=tof.start()
   udp = sk.UDP_Send(sk.learning_machine,sk.sensor_port)
   
   STEP=20
   HANDLE_STEP=15

   PERIOD=0.1
   
   right_flag = 0
   left_flag = 0

   ssr3=ctrl.KeyAssign()   
 
   key = keyin.Keyboard()
   ch="c"
   print("Input q to stop.")
   now=time.time()
   start=now
   init=now
   count=0
   left=0
   right=0
   while ch!="q":
      ch = key.read()

      distL=tofL.get_distance()
      distR=tofR.get_distance()

      left,right,angl=ssr3.update(ch,distL,distR)

      camera.cam.capture(camera.rawCapture, format="bgr", use_video_port=True)
      frame = camera.rawCapture.array

      # Send data to learning server only when you have key-input.
      if ch!='':
         Send(frame,left,right)
      
      show=cv2.resize(frame,(800,400))
      cv2.imshow('front',show[view_upper:view_lower,:,:])
      cv2.waitKey(1)

      try:
            
         # Update in PERIOD
         if now-init>PERIOD:
            rate=int(count/PERIOD)
            print("\r time:%8.2f %5d %5d %5d %s" % (now-start,rate,left,right,ch),end='')
            init=now
            count=0
         
      except KeyboardInterrupt:
         ssr3.stop()
         break

      camera.rawCapture.truncate(0)
      now=time.time() 
      count+=1

   print("\n Bye-bye!")
   ssr3.stop()
   
