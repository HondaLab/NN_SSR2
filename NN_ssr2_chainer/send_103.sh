#!/usr/bin/expect

set timeout 9
spawn scp Input_data_max.csv Output_data_max.csv disdata_num_weight.csv history_data_step_num.csv optimum_weight_1000 optimum_weight_2000 pi@172.16.7.103:/home/pi/NN_SSR2/NN_ssr2_chainer
expect "s password:"
send "ssr2\n"
interact
