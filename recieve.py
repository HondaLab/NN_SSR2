#!/usr/bin/python3
import modules.li_socket as sk
import modules.keyin as keyin
import socket
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

PERIOD=0.1

udp = sk.UDP_Recv(sk.learning_machine,sk.sensor_port)
data = [0]
teacher_data_list = []

key = keyin.Keyboard()
ch = 'c'
data_number = 0
now=time.time()
start=now
init=now
count=0
print("Input 'q' to stop.")
print("time   rate   data_num")
while ch !='q':
    try:
        data = udp.recv()
        data_number = data_number + 1
        teacher_data_list.append(data)
    except (BlockingIOError,socket.error):
        time.sleep(0.0001)

    if now-init>PERIOD:
        rate=count/PERIOD
        print("\r %5.2f %5.2f %d" % (now-start,rate,data_number),end='')
        count=0
        init=now

    count+=1
    now=time.time()
    ch = key.read()

f1 = open('/tmp/chainer_data_in.csv','a+',encoding='utf-8')
csv_writer1 = csv.writer(f1) 
f2 = open('/tmp/chainer_motor_out.csv','a+',encoding='utf-8')
csv_writer2 = csv.writer(f2) 
f3 = open('/tmp/chainer_data_in_include_distance_data.csv','a+',encoding='utf-8')
csv_writer3 = csv.writer(f3) 

for i in range(0,len(teacher_data_list)):
    dd = teacher_data_list[i]
    csv_writer1.writerow(dd[0:960])
    csv_writer2.writerow(dd[963:965])  # 964:965?
    csv_writer3.writerow(dd[0:963]) 

f1.flush() 
f1.close() 
f2.flush() 
f2.close() 
f3.flush() 
f3.close() 
print("data 保存完了")
