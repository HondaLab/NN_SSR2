#!/usr/bin/python3

# you need
# sudo pigpiod

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.socket as sk
import modules.tof4_6a as tof 
import modules.ssr3 as ssr3
import pigpio
import cv2

import socket
import time


if __name__=="__main__":
   
   #tofR,tofL,tofC,tofM=tof.start()
   controller=sk.UDP_Recv(sk.robot_addr,sk.robot_port)
   control_data=[4]
   motor_udp=sk.UDP_Send(sk.learning_addr,sk.motor_port)
   motor_data=[5]

   body=ssr3.Actuator()   

   PERIOD=0.02

   distL=0
   distC=0
   distR=0

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
      #distC=tofC.get_distance()
      #distR=tofR.get_distance()
      try:
         control_data=controller.recv()
         Lx=control_data[0]
         Ly=control_data[1]
         Rx=control_data[2]
         Ry=control_data[3]
         joystick=[Lx,Ly,Rx,Ry]
         left,right=body.run(joystick)
         motor_data=[distL,distC,distR,left,right]
      except (BlockingIOError, socket.error):
         pass


      try: # show infomation
         if now-init>PERIOD:
            rate=int(count/PERIOD)
            print("\r time:%8.2f rate:%5d left:%5d right:%5d" % (now-start,rate,left,right),end='')
            motor_udp.send(motor_data)
            init=now
            count=0
         
      except KeyboardInterrupt:
         break

      now=time.time() 
      count+=1

   print("\n Bye-bye!")
   body.stop()
   
