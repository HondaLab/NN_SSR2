import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import cv2
import random
import csv

def RGB_Entropy(RGB):
    P_i = []
    for z in range(np.min(RGB),np.max(RGB),1):
        z_num = 0
        for c in range(0,RGB.shape[0]):
            for v in range(0,RGB.shape[1]):
                for b in range(0,RGB.shape[2]):
                    if RGB[c,v,b] == z:
                        z_num = z_num + 1
        P_i.append(z_num/(RGB.shape[0]*RGB.shape[1]*RGB.shape[2]))
        H = 0
        for u in range(0,len(P_i)):
            if P_i[u]>0:
                H = H + (P_i[u]*(math.log(P_i[u],2)))
    entropy_result = -H
    return entropy_result

robot_list = ["101","102","104","105","106","108","111","112"]
entro_list = []
entropy_mat = np.zeros((len(robot_list),3))
image_num = 0
whileloop_num = 0
while_loop_stop = 100
for i in range(len(robot_list)):
    path = "robot_perspective_flim_" + robot_list[i] + ".mp4"
    cap = cv2.VideoCapture(path)
    while(cap.isOpened()):
        try:
            ret,frame = cap.read()
            entro_list.append(RGB_Entropy(frame))
            whileloop_num = whileloop_num +1
            if whileloop_num > while_loop_stop:
                break
        except:
            print(whileloop_num)
    entropy_mat[i,0] = np.min(entro_list)
    entropy_mat[i,1] = np.max(entro_list)
    entropy_mat[i,2] = np.mean(entro_list)

print("    min","     ","max","     ","mean") 
print(entropy_mat)

f = open('Entropy_Data.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)   
for o in range(0,entropy_mat.shape[0]):   
    csv_writer.writerow(entropy_mat[0,:])        
f.close()

cap.release()
cv2.destroyAllWindows()


