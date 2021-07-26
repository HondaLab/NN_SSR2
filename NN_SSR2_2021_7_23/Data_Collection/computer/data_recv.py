import socket
import modules.li_socket as sk
import time
import modules.keyin as keyin
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

computer_address = '172.16.7.19'
sensor_port = 50005


folder = '../../Learning'


udp = sk.UDP_Recv(computer_address,sensor_port)

data = [0]
start = time.time()
key = keyin.Keyboard()
ch = 'c'
data_number = 0

teacher_data_list = []

while 1:
    ch = key.read()
    if ch == "q":

        f1 = open(folder+'/'+'chainer_data_in.csv','w',encoding='utf-8')
        csv_writer1 = csv.writer(f1) 
        f3 = open(folder+'/'+'chainer_data_in_include_distance_data.csv','w',encoding='utf-8')
        csv_writer3 = csv.writer(f3) 
        f2 = open(folder+'/'+'chainer_motor_out.csv','w',encoding='utf-8')
        csv_writer2 = csv.writer(f2) 
        for i in range(0,len(teacher_data_list)):
            dd = teacher_data_list[i]
            csv_writer1.writerow(dd[0:960])
            csv_writer3.writerow(dd[0:963])
            csv_writer2.writerow(dd[963:965])

        f1.close() 
        f2.close()
        f3.close() 
        print('\n',"data 保存完了")


        break
    try:
        data = udp.recv()
        data_number = data_number + 1
        teacher_data_list.append(data)
        print("\r",end='')
        print("data got : ",data_number,end = '')
    except (BlockingIOError,socket.error):
        time.sleep(0.0001)



