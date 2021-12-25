#!/usr/bin/python3

# ssr3.py
# Yasushi Honda 2021 12/25


import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor as mt # pwmでモーターを回転させるためのモジュール. calibrated
import numpy as np
import time

class Actuator():

   def __init__(self):
      self.mL=mt.Lmotor(17)
      self.mR=mt.Rmotor(18)

   def run(self,joystick):

      Lx=joystick[0]
      Ly=joystick[1]
      Rx=joystick[2]
      Ry=joystick[3]


      left=-70*Ry+50*Rx
      right=-70*Ry-50*Rx

      if left<-100: left = -100
      if left>100: left = 100
      self.mL.run(left)
      if right<-100: right = -100
      if right>100: right = 100
      self.mR.run(right)

      return left, right

   def stop(self):
      self.mL.run(0)
      self.mR.run(0)



if __name__=="__main__":

   SLEEP=0.1
   ssr3=SsrRc()

   key = keyin.Keyboard()
   ch="c"
   print("Input q to stop.")
   while ch!="q":
      ch = key.read()
      try:
         ssr3.update(ch)
         time.sleep(SLEEP)
      except KeyboardInterrupt:
         ssr3.stop()
         break

   print("\nTidying up")
   ssr3.stop()
