#!/usr/bin/python3
# ssr2_rc2a.py
# CC BY-SA Yasushi Honda 2020 2/25 
# How to execute
# sudo pigpiod
# pyhton3 hjkl1.py 
import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as motor5a # pwmでモーターを回転させるためのモジュール
#import modules.vl53_4a as lidar
import modules.camera as camera
import modules.imageCut as ic
import pigpio
from subprocess import Popen
import numpy as np
import cv2
#import sock4robot_7a as sk
# Resolution of camera ex. 640x480, 320x240

class input_data:
   def __init__(self,X,Y):
      self.r = np.zeros((X,Y))
      self.g = np.zeros((X,Y))
      self.b = np.zeros((X,Y))
      
data_num = 10
in_data = [input_data(camera.RES_X,camera.RES_Y) for i in range(data_num)]
in_data_posi = 0

f1 = open("opencv_data_in1.csv","w")
f1.write("one")
f1.write('\t')
f1.write("two")
f1.write('\t') 
f1.write("three")
f1.write('\n') 

f2 = open("opencv_data_in2.csv","w")
f2.write("one")
f2.write('\t')
f2.write("two")
f2.write('\t') 
f2.write("three")
f2.write('\n') 

f3 = open("opencv_data_in3.csv","w")
f3.write("one")
f3.write('\t')
f3.write("two")
f3.write('\t') 
f3.write("three")
f3.write('\n') 


f4 = open("opencv_data_out.csv","w")
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
      camera.cam.capture(camera.rawCapture, format="bgr", use_video_port=True)
      frame = camera.rawCapture.array
      cv2.imshow('frame',frame[ic.img_cut_top:ic.img_cut_below,:,:])
      cv2.waitKey(1)
      in_data[in_data_posi].r = frame[ic.img_cut_top:ic.img_cut_below,:,0]
      in_data[in_data_posi].g = frame[ic.img_cut_top:ic.img_cut_below,:,1]
      in_data[in_data_posi].b = frame[ic.img_cut_top:ic.img_cut_below,:,2]
   
      left_motor = str(l)
      f4.write(left_motor)
      f4.write('\t')
      right_motor = str(r)
      f4.write(right_motor)
      f4.write('\n')
      camera.rawCapture.truncate(0)
   else:
      print('The data space is full')

if __name__=="__main__":
   STEP=20
   HANDLE_STEP=19
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
            
      except KeyboardInterrupt:
         mL.run(0)
         mR.run(0)
         break

   print("\nTidying up")
   mL.run(0)
   mR.run(0)
   print('printing data, It will cost a few minutes,Please wait a moment')
   for k in range(0,data_num):
      for i in range(0,ic.img_cut_below-ic.img_cut_top):
         for j in range(0,camera.RES_Y):
            f1.write(str(in_data[k].r[i,j]))
            f1.write('\t')
            f2.write(str(in_data[k].g[i,j]))
            f2.write('\t')
            f3.write(str(in_data[k].b[i,j]))
            f3.write('\t')
         f1.write('\n')
         f2.write('\n')
         f3.write('\n')
         
      f1.write('M')
      f1.write('\n')
      f2.write('M')
      f2.write('\n')
      f3.write('M')
      f3.write('\n')
      
   print('printing data is finished')
