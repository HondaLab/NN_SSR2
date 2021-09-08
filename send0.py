#!/usr/bin/expect
addr=172.16.7.109

set timeout 9
spawn scp Input_data_max.csv Output_data_max.csv optimum_weight_1000 pi@$addr:/home/pi/NN_SSR2/NN_ssr2_chainer
expect "s password:"
send "ssr2\n"
interact
