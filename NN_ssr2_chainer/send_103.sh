#!/usr/bin/expect

set timeout 9
spawn scp Input_data_max.csv Output_data_max.csv optimum_weight_1000 pi@172.16.7.103:/home/pi/NN_ssr2_chainer
expect "s password:"
send "ssr2\n"
interact
