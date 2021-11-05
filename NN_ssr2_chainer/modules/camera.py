
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

RES_X=int( 320 )
RES_Y=int( 240 )
cam = PiCamera()
cam.framerate = 20
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
