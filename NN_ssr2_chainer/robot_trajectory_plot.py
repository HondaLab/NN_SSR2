#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import pandas as pd
import math
import os
from pathlib import Path


xlimit = 50
point_size = 1
figsize_x = 50
figsize_y = 50
fosz = 40
time_R_fosz = 100
lenged_fosz = 20
figure_num = 0
#robot_list = ["101","102","103","104","105","106","111","112"]
#robot_list = ["103","108"]
#robot_list = ["rpi120"]
#robot_list = ["108_take4"]
#robot_list = ["108_ref1","108_ref2","108_ref3","108_ref4","108_ref5","108_ref6","108_ref7","108_ref8","108_ref9","108_ref10"]
#robot_list = ["108_ang_90s"]
#robot_list = ["0518_8_t1-B"]
file_list = os.listdir()
trc_list = [f for f in file_list if '.trc' in f]
name_list = []

for p in trc_list:
   name = Path(p).stem
   name_list.append(name)


for j in range(len(trc_list)):
    
    figure_num = figure_num + 1
    #path = "locus_"+robot_list[j]+".trc"
    path = trc_list[j]

    with open(path,encoding="utf-8",errors='ignore',mode="r") as f:
        locus_ssr103 = f.readlines()

    data_103 = np.zeros((len(locus_ssr103)-6,3))
    l103_time = []
    l103_shita = []
    l103_R = []
    x = []
    y = []
    #d = [-2000*1.9251369913182816,0,2000*1.9251369913182816]
    #c = [-2000.0,0,2000.0]

    for i in range(6,data_103.shape[0]):
        l3 = locus_ssr103[i].split("\t")
        print(l3)
        try:
            l3x = (float(l3[2])+float(l3[5])+float(l3[8])+float(l3[11])+float(l3[14]))/5
            l3y = (float(l3[3])+float(l3[6])+float(l3[9])+float(l3[12])+float(l3[15]))/5
            data_103[i,0] = float(l3[1])
            data_103[i,1] = float(l3x)
            data_103[i,2] = float(l3y)
            l103_time.append(data_103[i,0])
            #if 2 <= data_103[i,0] <= 70:
                #x.append(data_103[i,1])
                #y.append(data_103[i,2])
            x.append(data_103[i,1])
            y.append(data_103[i,2])
            if data_103[i,1]>0 and data_103[i,2]>0:
                shita = math.atan(data_103[i,2]/data_103[i,1])
            if data_103[i,1]<0 and data_103[i,2]>0:
                shita = math.atan(-data_103[i,1]/data_103[i,2])+((math.pi)/2)
            if data_103[i,1]>0 and data_103[i,2]<0:
                shita = -math.atan(-data_103[i,2]/data_103[i,1])
            if data_103[i,1]<0 and data_103[i,2]<0:
                shita = -math.atan(data_103[i,1]/data_103[i,2])-((math.pi)/2)
            l103_shita.append(shita)
            l103_R.append(np.sqrt((data_103[i,1]/10)**2 + (data_103[i,2]/10)**2))
        except:
            data_103[i,0] = data_103[i-1,0]
            data_103[i,1] = data_103[i-1,1]
            data_103[i,2] = data_103[i-1,2]
            l103_time.append(data_103[i,0])
            l103_shita.append(l103_shita[-1])
            l103_R.append(l103_R[-1])
    
    
    
    plt.figure(figure_num)
    #fig = plt.figure()
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    
    ax = fig.add_subplot(212)
    #ax.scatter(l103_time,l103_R,color='r',s=point_size,label="103")
    #ax.scatter(data_108_time,l108_R,color='k',s=point_size,label="108")
    ax.plot(x,y,color='r',label="robot")
    #ax.plot(c,d,color='r',label="graph")

    #ax.plot(l103_time,l103_R,color='r',label="robot NO.3")
    #ax.plot(data_108_time,l108_R,color='k',label="robot NO.8")
    #plt.legend(loc='lower left',fontsize=lenged_fosz)
    '''#擬楕円コース
    ellipse1 = patches.Wedge(
    center=(0,800),
    r=350,
    theta1=0,
    theta2=180,
    width=None,
    color="blue"
    )
    ax.add_patch(ellipse1)
    
    ellipse2 = patches.Wedge(
    center=(0,-800),
    r=350,
    theta1=180,
    theta2=360,
    width=None,
    color="blue"
    )
    ax.add_patch(ellipse2)
    
    ellipse3 = patches.Rectangle(
    xy=(-350,-800),
    width=700,
    height=1600,
    color="blue"
    )
    ax.add_patch(ellipse3)
    
    patch = plt.Circle(
    xy=(0, 0),  # 　中心
    radius=1000,  # 半径
    fill=True,  # 塗りつぶし
    )
    ax.add_patch(patch)

    patch = plt.Circle(
    xy=(0, 0),  # 　中心
    radius=2000,  # 半径
    fill=False,  # 塗りつぶし無し
    )
    ax.add_patch(patch)
    '''
    
    plt.axis([-2000,2000,-2000,2000])
    plt.grid()
    #plt.minorticks_on()
    #plt.grid(which = "minor", axis="x")
    plt.title("robot motion",fontsize=time_R_fosz)
    plt.xlabel("x(mm)",fontsize=time_R_fosz)
    plt.ylabel("y(mm)",fontsize=time_R_fosz)
    #ax.set_xlim(0,xlimit)
    #ax.set_ylim(110,190)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    
    ax.set_aspect('equal',adjustable='box')

    #ax = fig.add_subplot(211)
    #ax.scatter(l103_time,l103_shita,s=point_size,color='r',label="robot NO.3")
    #ax.plot([0,l103_time[-1]],[0,0],color='b')
    #ax.scatter(data_108_time,l108_shita,color='k',s=point_size,label="robot NO.8")
    #plt.xlabel("Time[s]",fontsize=time_R_fosz)
    #plt.ylabel(chr(952),fontsize=time_R_fosz)
    #plt.grid()
    #plt.legend(loc='lower left',fontsize=lenged_fosz,scatterpoints=90)
    #ax.set_xlim(0,xlimit)
    #plt.xticks(fontsize=fosz)
    #plt.yticks(fontsize=fosz)

    plt.savefig(name_list[j]+'_trajectory.jpg',bbox_inches='tight')
    
    """
    plt.figure(figure_num)
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    plt.plot(l103_time,l103_R,color='r',label="robot NO.3")
    plt.grid()
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel("R[cm]",fontsize=time_R_fosz)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    plt.savefig(robot_list[j]+'_R.eps',bbox_inches='tight')

    """
    """
    plt.figure(figure_num)
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    plt.scatter(l103_time,l103_shita,s=point_size,color='r',label="robot NO.3")
    plt.plot([0,l103_time[-1]],[0,0],color='b')
    #ax.scatter(data_108_time,l108_shita,color='k',s=point_size,label="robot NO.8")
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel(chr(952),fontsize=time_R_fosz)
    plt.grid()
    #plt.legend(loc='lower left',fontsize=lenged_fosz,scatterpoints=90)
    #ax.set_xlim(0,xlimit)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    plt.savefig(robot_list[j]+'_shita.eps',bbox_inches='tight')
    """
    
