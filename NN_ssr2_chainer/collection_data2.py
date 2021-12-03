#!/usr/bin/python3

# ssr2_rc2a.py
# CC BY-SA Yasushi Honda 2020 2/25 

# How to execute
# sudo pigpiod
# pyhton3 hjkl1.py 

import modules.keyin as keyin # キーボード入力を監視するモジュール
import modules.motor5a as mt # pwmでモーターを回転させるためのモジュール
import modules.imageCut as ic
import cv2
import pigpio
from subprocess import Popen
import numpy as np
import modules.vl53_5a as lidar
import socket
import modules.li_socket as sk
import time
import modules.camera as camera

tofL,tofR,tofC=lidar.start()

picture_data = []

def Run(mL,mR,left,right):
    if left<-100: left = -99
    if left>100: left = 99
    if right<-100: right = -99
    if right>100: right = 99
    mL.run(left)
    mR.run(right)

def send_data(frame,l,r,vw):
    frame2 = frame[ic.im_cut_up:ic.im_cut_below,:,:]
    vw.write(frame2)
    for i in range(0,camera.RES_X):
       picture_data.append(sum(frame[ic.im_cut_up:ic.im_cut_below,i,0]))
    for i in range(0,camera.RES_X):
       picture_data.append(sum(frame[ic.im_cut_up:ic.im_cut_below,i,1]))
    for i in range(0,camera.RES_X):
       picture_data.append(sum(frame[ic.im_cut_up:ic.im_cut_below,i,2]))

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
    picture_data.append(distanceL)
    picture_data.append(distanceC)
    picture_data.append(distanceR)
    if l<-100: l = -99
    if l>100: l = 99
    if r<-100: r = -99
    if r>100: r = 99
    picture_data.append(l)
    picture_data.append(r)
    udp_send_data.send(picture_data)
    picture_data.clear()

if __name__=="__main__":
    OUT_FILE="data_collection_output.avi"
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    record_fps=10
    crop_width=320
    crop_height= ic.im_cut_below - ic.im_cut_up
    print("\n# Resolution: %5d x %5d" % (crop_width,crop_height))
    crop_size = (crop_width, crop_height)
    vw = cv2.VideoWriter(OUT_FILE, fmt, record_fps, crop_size)
    udp_send_data = sk.UDP_Send(sk.data_reciving_terminal,sk.sensor_port)
   
    STEP = 35
    HANDLE_STEP = 35 

    CSV_TRIM=95
   
    right_flag = 0
    left_flag = 0

    mL=mt.Lmotor(23)
    mR=mt.Rmotor(14)
    csv=mt.Rmotor(18)
    csv.run(CSV_TRIM)
   
    key = keyin.Keyboard()
    ch="c"
    PERIOD=0.2
    now = time.time()
    start = now
    init = now
    count=0
    send_data_count=0
    print("# Input q to stop.")
    left=0
    right=0
    print("#   time,left,right,rate,send_data")
    while ch!="q":
        try: # KeyboardInterrupt
            try: # cam.capture
               camera.cam.capture(camera.rawCapture, format="bgr", use_video_port=True)
               frame = camera.rawCapture.array
               cv2.imshow('frame',frame)
               cv2.waitKey(1)

               if ch == "w" :
                  left += STEP
                  right += STEP
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)
               if ch == "s" :
                  left -= STEP
                  right -= STEP
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)
               if ch == "a" :
                  left = -(STEP*1.6)
                  right = -(STEP*1.6)
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)
               if ch == "d" :
                  left = 0
                  right = 0
                  Run(mL,mR,left,right)
               if ch == "j" :
                  left = left - HANDLE_STEP
                  left_flag = left_flag - HANDLE_STEP
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)
               if ch == "k" :
                  right = right - right_flag
                  left = left - left_flag
                  right_flag = 0
                  left_flag = 0
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)
               if ch == "l" :
                  right = right - HANDLE_STEP
                  right_flag = right_flag - HANDLE_STEP
                  send_data(frame,left,right,vw)
                  send_data_count+=1
                  Run(mL,mR,left,right)

            except:
               pass
                
        except KeyboardInterrupt:
            mL.run(0)
            mR.run(0)
            break

        now=time.time()
        if now-start>PERIOD:        
           rate=int(count/PERIOD)
           print("\r %7.1f %4d %4d %5d %5d" % (now-init,left,right,rate,send_data_count),end='')
           count=0
           start=now
           
        count+=1
        camera.rawCapture.truncate(0)
        ch = key.read()

    print("\n See your again!")
    vw.release()
    mL.run(0)
    mR.run(0)
    csv.run(CSV_TRIM)
   
