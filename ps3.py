#!/usr/bin/python3
# Yasushi Honda 2021 12/23
# PS3のジョイスティック値を読み込んで、raspi にソケットで送る。
import pygame
import time
from pygame.locals import *
import modules.socket as sk
import modules.keyin as kin

PERIOD=0.5

# ジョイスティックの初期化
pygame.joystick.init()
try:
   # ジョイスティックインスタンスの生成
   x = pygame.joystick.get_count()
   print("Joystick count:%3d" % x)
   joystick = pygame.joystick.Joystick(x-1)
   joystick.init()
   print('ジョイスティックの名前:', joystick.get_name())
   print('ボタン数 :', joystick.get_numbuttons())
except pygame.error:
   print('ジョイスティックが接続されていません')

# pygameの初期化
pygame.init()

# 画面の生成
screen = pygame.display.set_mode((320, 320))

message="ジョイステックの値を %s に送信します"
print(message % sk.robot_addr)
udp=sk.UDP_Send(sk.robot_addr,sk.robot_port)
data=[]
key=kin.Keyboard()
now=time.time()
start=now
init=now
count=0
ch='c'
while ch!='q':
   now=time.time()
   # イベントの取得
   for e in pygame.event.get():

       # ジョイスティックのボタンの入力
       if e.type == pygame.locals.JOYAXISMOTION:
           print("\r send rate:%3d Lx:%8.5f Ly:%8.5f Rx:%8.5f Ry:%8.5f" % (count,joystick.get_axis(0),joystick.get_axis(1),joystick.get_axis(3),joystick.get_axis(4)), end='')
           data.append(joystick.get_axis(0))
           data.append(joystick.get_axis(1))
           data.append(joystick.get_axis(3))
           data.append(joystick.get_axis(4))
           count+=1
           udp.send(data)
           data.clear()
       '''
       elif e.type == pygame.locals.JOYBUTTONDOWN:
           print('ボタン'+str(e.button)+'を押した')
       elif e.type == pygame.locals.JOYBUTTONUP:
           print('ボタン'+str(e.button)+'を離した')
       '''

   if now-start>PERIOD:
      rate=int(count/PERIOD)
      count=0
      start=now

   ch=key.read()

print("\n")
