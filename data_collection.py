import modules.li_socket as sk
import modules.keyin as keyin
import socket
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

udp = sk.UDP_Recv(sk.learning_machine,sk.sensor_port)
data = [0]
teacher_data_list = []

key = keyin.Keyboard()
ch = 'c'
data_number = 0
while ch !='q':
    try:
        data = udp.recv()
        data_number = data_number + 1
        teacher_data_list.append(data)
        print("data got : ",data_number)
    except (BlockingIOError,socket.error):
        time.sleep(0.0001)
    ch = key.read()

f = open('chainer_data_in.csv','w',encoding='utf-8')
csv_writer1 = csv.writer(f) 
f2 = open('chainer_motor_out.csv','w',encoding='utf-8')
csv_writer2 = csv.writer(f2) 
for i in range(0,len(teacher_data_list)):
    dd = teacher_data_list[i]
    csv_writer1.writerow(dd[0:960])
    csv_writer2.writerow(dd[960:962]) 
f.close() 
f2.close() 
print("data 保存完了")
