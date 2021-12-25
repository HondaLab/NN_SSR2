#!/usr/bin/python3

# motor5a.py
# Calibrated by tanh function
# 2021 4/17
# Yasushi Honda

import pigpio
import numpy as np

MIN_WIDTH=1000
MID_WIDTH=1500
MAX_WIDTH=2000

class Motor:

   def __init__(self,gpio):
      self.gpio=gpio
      self.pi = pigpio.pi()
      if not self.pi.connected:
         exit()
      self.pi.set_servo_pulsewidth(gpio, MID_WIDTH)

   def output(self,power):
      puls=MID_WIDTH+power
      if puls>MIN_WIDTH and puls<MAX_WIDTH:
         self.pi.set_servo_pulsewidth(self.gpio, puls)

   def stop(self):
      self.output(0)
      self.pi.stop()

class Lmotor(Motor):
   def run(self,power):
      output=62*np.arctanh(-power/101)+6*np.sign(-power)
      self.output(output)

class Rmotor(Motor):
   def run(self,power):
      output=62*np.arctanh(power/101)+6*np.sign(power)
      self.output(output)

class Servo(Motor):
   def move(self,power):
      gain=3.0
      trim=120
      output=int(gain*power)+trim
      self.output(output)

