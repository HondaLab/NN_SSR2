#!/usr/bin/python3
import socket
import modules.li_socket as sk
import time
import modules.keyin as keyin
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import sys

data_name = input("Please input the last name of data (Arabic numerals) : ")
data_num_limit = input("How many data do you want recive : ")
udp = sk.UDP_Recv(sk.data_reciving_terminal,sk.sensor_port)

data = [0]
start = time.time()
data_number = 0
teacher_data_list = []

while 1:
    if data_number >= int(data_num_limit):
        
        f1 = open('part_data_in' + str(data_name) + '.csv','w',encoding='utf-8')
        csv_writer1 = csv.writer(f1) 
        f3 = open('part_data_in_include_distance_data' + str(data_name) + '.csv','w',encoding='utf-8')
        csv_writer3 = csv.writer(f3) 
        f2 = open('part_motor_out' + str(data_name) +'.csv','w',encoding='utf-8')
        csv_writer2 = csv.writer(f2) 
        for i in range(0,len(teacher_data_list)):
            dd = teacher_data_list[i]
            csv_writer1.writerow(dd[0:960])
            csv_writer3.writerow(dd[0:963])
            csv_writer2.writerow(dd[963:965])
        time.sleep(1)
        f1.close() 
        f2.close()
        f3.close() 
        time.sleep(1)
        print('\n',"data 保存完了")
        
        break
    try:
        data = udp.recv()
        data_number = data_number + 1
        teacher_data_list.append(data)
        #print("\r",end='')
        print("data got : ",data_number,end = '')
        print("\r",end='')
    except (BlockingIOError,socket.error):
        time.sleep(0.0001)

