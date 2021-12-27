#!/usr/bin/python3
import socket
import modules.socket as sk
import time
import modules.keyin as keyin
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import sys

PERIOD=0.03

data_name = input("Please input the last name of data (Arabic numerals) : ")
data_num_limit = input("How many data do you want recive : ")
picam_udp = sk.UDP_Recv(sk.learning_addr,sk.picam_port)
motor_udp = sk.UDP_Recv(sk.learning_addr,sk.motor_port)

data = []
motor_data = []
now=time.time()
start=now
init=now
data_number = 0
teacher_data_list = []

while data_number < int(data_num_limit):
   try:
      data = picam_udp.recv()
      data_number = data_number + 1
      teacher_data_list.append(data)
      teacher_data_list.append(motor_data)
   except (BlockingIOError,socket.error):
      pass
   try:
      motor_data = motor_udp.recv()
   except (BlockingIOError,socket.error):
      pass

   now=time.time()
   if now-start>PERIOD:
      print("\r %5d left:%5.1f right:%5.1f" %(data_number,motor_data[3],motor_data[4]),end = '')
      start=now

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
f1.close() 
f2.close()
f3.close() 
print('\n',"data 保存完了")
