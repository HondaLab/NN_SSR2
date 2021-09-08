#!/usr/bin/sh
addr=172.16.7.109
file1=/tmp/data_in_max.csv
file2=/tmp/data_out_max.csv
file3=/tmp/optimum_weight_1100

sshpass -p ssr2 scp $file1 $file2 $file3 pi@$addr:/tmp/
