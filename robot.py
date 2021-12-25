#!/usr/bin/python3

# you need
# sudo pigpiod

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.socket as sk
import modules.tof4_6a as tof 
import modules.picam as picam 
import modules.ssr3 as ssr3
import pigpio
import cv2

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
   
   #tofR,tofL,tofC,tofM=tof.start()
   learning = sk.UDP_Send(sk.learning_addr,sk.learning_port)
   controller=sk.UDP_Recv(sk.robot_addr,sk.robot_port)
   control_data=[4]

   body=ssr3.Actuator()   

   cam=picam.PI_CAMERA(320,240)
   
   PERIOD=0.5

   OUT_FILE="/tmp/output.avi"
   print("# Captured movie is written in %s ." % OUT_FILE)
   fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
   record_fps=30
   crop_w=320
   crop_h=240
   vw = cv2.VideoWriter(OUT_FILE, fmt, record_fps, (crop_w,crop_h))
   
   right_flag = 0
   left_flag = 0

 
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

      #distL=tofL.get_distance()
      #distR=tofR.get_distance()
      try:
         control_data=controller.recv()
         Lx=control_data[0]
         Ly=control_data[1]
         Rx=control_data[2]
         Ry=control_data[3]
         joystick=[Lx,Ly,Rx,Ry]
         left,right=body.run(joystick)
      except (BlockingIOError, socket.error):
         pass

      frame = cam.capture()

      # Send data to learning server only when you have key-input.
      #if ch!='':
      #   Send(frame,left,right)
      
      show=cv2.resize(frame,(800,400))
      cv2.imshow('front',show[view_upper:view_lower,:,:])
      vw.write(frame)
      cv2.waitKey(1)

      try: # show infomation
         if now-init>PERIOD:
            rate=int(count/PERIOD)
            print("\r time:%8.2f rate:%5d left:%5d right:%5d" % (now-start,rate,left,right),end='')
            init=now
            count=0
         
      except KeyboardInterrupt:
         break

      now=time.time() 
      count+=1

   vw.release()
   print("\n Bye-bye!")
   body.stop()
   
