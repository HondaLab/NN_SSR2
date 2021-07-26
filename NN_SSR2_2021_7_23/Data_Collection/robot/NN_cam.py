
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
import numpy as np
import modules.keyin as keyin # キーボード入力を監視するモジュール
import time


RES_X=int( 320 )
RES_Y=int( 320 )
cam = PiCamera()
cam.framerate = 10
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

im_cut_up = 172
im_cut_below = 236

key = keyin.Keyboard()
ch = 'c'
while ch != 'q':
    ch = key.read()
    cam.capture(rawCapture, format="bgr", use_video_port=True)
    frame = rawCapture.array
    cv2.imshow('frame',frame[im_cut_up:im_cut_below,:,:])
    cv2.waitKey(1)
    print("\r",end='')
    print('filming',end = '')
    rawCapture.truncate(0)
    
print('stop')



