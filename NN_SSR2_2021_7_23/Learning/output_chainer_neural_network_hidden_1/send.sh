#!/usr/bin/expect

set timeout 9
spawn scp data_in_max.csv data_out_max.csv optimum_weight_1000 pi@172.16.7.103:/home/pi/NN_SSR2_2021_7_23/Autonomous_Movement/anticlockwise/hidden1
expect "s password:"
send "ssr2\n"
interact
