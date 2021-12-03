
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math


xlimit = 500
ylimit_up = 200
ylimit_down = 100
ylimit_shita_up = 3.15
ylimit_shita_down = -3.15
point_size = 1
figsize_x = 50
figsize_y = 16
fosz = 30
time_R_fosz = 50
lenged_fosz = 20
figure_num = 0
robot_list = ["101","102","104","105","106","108","111","112"]

for j in range(len(robot_list)):
    
    figure_num = figure_num + 1
    path = "locus_"+robot_list[j]+".trc"

    with open(path) as f:
        locus_ssr = f.readlines()

    data = np.zeros((len(locus_ssr)-6,3))
    time = []
    shita_list = []
    R = []

    for i in range(6,data.shape[0]):
        l = locus_ssr[i].split("\t")
        try:
            lx = (float(l[2])+float(l[5])+float(l[8])+float(l[11])+float(l[14]))/5
            ly = (float(l[3])+float(l[6])+float(l[9])+float(l[12])+float(l[15]))/5
            data[i,0] = float(l[1])
            data[i,1] = float(lx)
            data[i,2] = float(ly)
            time.append(data[i,0])
            if data[i,1]>0 and data[i,2]>0:
                shita = math.atan(data[i,2]/data[i,1])
            if data[i,1]<0 and data[i,2]>0:
                shita = math.atan(-data[i,1]/data[i,2])+((math.pi)/2)
            if data[i,1]>0 and data[i,2]<0:
                shita = -math.atan(-data[i,2]/data[i,1])
            if data[i,1]<0 and data[i,2]<0:
                shita = -math.atan(data[i,1]/data[i,2])-((math.pi)/2)
            shita_list.append(shita)
            R.append(np.sqrt((data[i,1]/10)**2 + (data[i,2]/10)**2))
        except:
            data[i,0] = data[i-1,0]
            data[i,1] = data[i-1,1]
            data[i,2] = data[i-1,2]
            time.append(data[i,0])
            shita_list.append(shita_list[-1])
            R.append(R[-1])
    
    plt.figure(figure_num)
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    ax = fig.add_subplot(211)
    ax.scatter(time,shita_list,s=point_size,color='r')
    ax.plot([0,time[-1]],[0,0],color='b')
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel(chr(952),fontsize=time_R_fosz)
    plt.grid()
    #plt.legend(loc='lower left',fontsize=lenged_fosz,scatterpoints=90)
    ax.set_xlim(0,xlimit)
    ax.set_ylim(ylimit_shita_down,ylimit_shita_up)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)


    ax = fig.add_subplot(212)
    ax.plot(time,R,color='r')
    #plt.legend(loc='lower left',fontsize=lenged_fosz)
    plt.grid()
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel("R[cm]",fontsize=time_R_fosz)
    ax.set_xlim(0,xlimit)
    ax.set_ylim(ylimit_down,ylimit_up)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    
    plt.savefig(robot_list[j]+'_shita_R.eps',bbox_inches='tight')
    
   
    """
    plt.figure(figure_num)
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    plt.scatter(time,shita_list,s=point_size,color='r')
    plt.plot([0,time[-1]],[0,0],color='b')
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel(chr(952),fontsize=time_R_fosz)
    plt.grid()
    #plt.legend(loc='lower left',fontsize=lenged_fosz,scatterpoints=90)
    ax.set_xlim(0,xlimit)
    ax.set_ylim(ylimit_shita_down,ylimit_shita_up)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    plt.savefig(robot_list[j]+'_shita.eps',bbox_inches='tight')
    """
    """
    plt.figure(figure_num)
    fig = plt.figure(figsize=(figsize_x,figsize_y))
    plt.plot(time,R,color='r')
    plt.grid()
    plt.xlabel("Time[s]",fontsize=time_R_fosz)
    plt.ylabel("R[cm]",fontsize=time_R_fosz)
    ax.set_xlim(0,xlimit)
    ax.set_ylim(ylimit_down,ylimit_up)
    plt.xticks(fontsize=fosz)
    plt.yticks(fontsize=fosz)
    plt.savefig(robot_list[j]+'_R.eps',bbox_inches='tight')

    """
