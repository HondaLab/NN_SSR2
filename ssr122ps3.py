#!/usr/bin/python3

# ssr3ps3.py recieve controll data from ps3
# Yasushi Honda 2021 12/23

# How to execute
# sudo pigpiod
# pyhton3 ssrXY.py 

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.rc4ps3 as rc
import modules.vl53_5a as tof
import modules.socket as sk
import socket
import time
import numpy as np

SLEEP=0.1
PERIOD=0.03
ssr3=rc.Assign()
#tofL,tofR,tofC,tofM=tof.start()

udp=sk.UDP_Recv(sk.robot,sk.port)
data=[4]
key = keyin.Keyboard()
ch="c"
print("##################################")
message="This recieves controll signal from 'ps3.py'."
print(message)
print("Input q to stop.")
print("##################################")
now=time.time()
init=now
start=now
print("left,right,angl,   Lx,   Ly,   Rx,   Ry")
while ch!="q":
   ch = key.read()
   try:
      data=udp.recv()
      Lx=data[0]
      Ly=data[1]
      Rx=data[2]
      Ry=data[3]
      '''
      distL=tofL.get_distance()
      distR=tofR.get_distance()
      distC=tofC.get_distance()
      distM=tofM.get_distance()
      dL=np.sqrt(distL*distC)
      dR=np.sqrt(distR*distC)
      '''
      distL=0
      distR=0
      left,right,angl=ssr3.update(Rx,Ry,distL,distR)
      now=time.time()
      if now-start>PERIOD:
         print("\r %4d %4d %4d %5.2f %5.2f %5.2f %5.2f" % (left,right,angl,data[0],data[1],data[2],data[3]),end='')
         start=now
      #time.sleep(SLEEP)
   except (BlockingIOError, socket.error):
      pass

print("\n Bye Bye!")
ssr3.stop()
