import socket
import li_socket as sk
import time
import keyin
import matplotlib.pyplot as plt
import numpy as np
import csv

udp = sk.UDP_Recv(sk.robot_address,sk.sensor_port)
data_limit = 4
data = [0]
start = time.time()
key = keyin.Keyboard()
ch = 'c'
u = 0

while 1:
    ch = key.read()
    if ch == "q":
        break
    try:
        data = udp.recv()
        print(data.shape)
    except (BlockingIOError,socket.error):
        time.sleep(0.0001)
        


