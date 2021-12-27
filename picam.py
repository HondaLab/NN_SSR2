#! /usr/bin/python3
# Yasushiu Honda 2021 9/8
# Capture frames from PiCamera and record them to /tmp 

import cv2
import time
import socket
import modules.socket as sk
import modules.keyin as keyin

from picamera.array import PiRGBArray
from picamera import PiCamera

RES_X=320
RES_Y=240

view_upper=170 # 170
view_lower=RES_Y

class PI_CAMERA():
   def __init__(self,width,height):
      
      # カメラの解像度 例：640x480, 320x240
      self.RES_X=int( width )
      self.RES_Y=int( height )
      
      # initialize the camera and grab a reference to the raw camera capture
      #カメラを初期化，カメラへのアクセス？ルート？オブジェクト作成？
      self.cam = PiCamera()
      self.cam.framerate = 30  #フレームレート
      self.cam.brightness = 50 #明るさ
      #cam.saturation = 50

      self.cam.awb_mode='auto'
      #list_awb = ['off', 'auto', 'sunlight', 'cloudy', 'shade']
      self.cam.iso=200
      self.cam.shutter_speed=10000000
      self.cam.exposure_mode = 'auto' # off, auto, fixedfps
      time.sleep(1)
      #self.g = self.cam.awb_gains
      #self.cam.awb_mode = 'off'
      #self.cam.awb_gains = self.g

      self.cam.resolution = (self.RES_X, self.RES_Y)
      self.cam.rotation=0
      self.cam.meter_mode = 'average' # average, spot, backlit, matrix
      self.cam.exposure_compensation = 0
      self.rawCapture = PiRGBArray(self.cam, size=(self.RES_X, self.RES_Y))

      self.rawCapture.truncate(0) # clear the stream for next frame

   def capture(self):
      tmp = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port="True")
      cap = next(tmp)
      frame = cap.array

      self.rawCapture.truncate(0) # clear the stream for next frame

      return frame

def Send(udp,frame):
   data=[]

   for x in range(0,RES_X):
      data.append(sum(frame[view_upper:view_lower,x,0]))
      data.append(sum(frame[view_upper:view_lower,x,1]))
      data.append(sum(frame[view_upper:view_lower,x,2]))

   udp.send(data)
   data.clear()


if __name__ == "__main__":

    recording='n'
    select='n'
    PERIOD=0.2

    picam_udp = sk.UDP_Send(sk.learning_addr,sk.picam_port)

    # For recording
    OUT_FILE="/tmp/output.avi"
    print("# Captured movie is written in %s ." % OUT_FILE)
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    record_fps=9
    width=RES_X
    height=RES_Y

    print("# Resolution: %5d x %5d" % (width,height))
    size = (width, height)
    crop_left = 0
    crop_right = width
    crop_upper = view_upper
    crop_lower = view_lower
    crop_h=crop_lower - crop_upper 
    crop_w=crop_right - crop_left
    print("# Crop: %5d x %5d" % (crop_w,crop_h))
    vw = cv2.VideoWriter(OUT_FILE, fmt, record_fps, (crop_w,crop_h))

    cam = PI_CAMERA(width,height)
    frame=cam.capture()
    if select=='y':
       bbox=cv2.selectROI(frame,False)
       print(bbox)

    key=keyin.Keyboard()
    ch='c'

    now=time.time()
    start=now
    init=now
    count=0
    print("# To stop, input 'q' in this terminal.")
    while ch!='q':
        now=time.time()
        ch=key.read()

        try: 
           capt = cam.capture()
           #print(len(v) for v in capt)
           frame = capt[crop_upper:crop_lower,crop_left:crop_right,:]
           frame = cv2.resize(frame,(crop_w,crop_h))
           show_size=(800,400)
           show=cv2.resize(frame,show_size)
           cv2.imshow("Front View", show)
           cv2.waitKey(1)
           if recording=='y':
              vw.write(frame)

           Send(picam_udp,frame)
           count+=1
      

        except KeyboardInterrupt:
           print("ctrl + C ")
           cv2.destroyAllWindows()
           vw.release()

        if now-start>PERIOD:
           rate=count/PERIOD
           print("\r time: %5.1f rate:%5.1f" % (now-init,rate), end='')
           count=0
           start=now

        #time.sleep(0.5)
           

    cv2.destroyAllWindows()
    vw.release()
    print("\n # Bye-bye \n")
